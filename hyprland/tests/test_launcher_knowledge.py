"""Behavior checks for units and bounded, cacheable dictionary lookups."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import launcher_knowledge as knowledge


class UnitTests(unittest.TestCase):
    def test_lengths_speeds_and_temperature(self):
        for query, expected in [('10 km to mile', 6.21371192237), ('10m/s to km/h', 36),
                                ('32 f to c', 0), ('100 c to f', 212), ('2 h to min', 120),
                                ('10 公里 转 英里', 6.21371192237)]:
            with self.subTest(query=query):
                result = knowledge.conversion(query)
                self.assertEqual(result.kind, 'conversion')
                self.assertAlmostEqual(float(result.target.split()[0]), expected, places=8)

    def test_bits_bytes_and_binary_prefixes_are_distinct(self):
        for query, expected in [('1 GB to MB', '1000 MB'), ('1 GiB to MiB', '1024 MiB'),
                                ('8 Mb to MB', '1 MB'), ('1 B to b', '8 b')]:
            with self.subTest(query=query):
                self.assertEqual(knowledge.conversion(query).target, expected)

    def test_dimensions_unknown_units_and_absolute_zero(self):
        for query in ('10 kg to km', '1 widget to m', '-274 c to k', '1e400 m to km'):
            self.assertEqual(knowledge.conversion(query).kind, 'error')
        for query in ('neovide', 'README.md', 'how to use tmux', '10 + 20'):
            self.assertIsNone(knowledge.conversion(query))


YOUDAO = {
    'ec': {'word': [{'usphone': 'ˌhaɪpəˈθetɪkəl', 'trs': [
        {'tr': [{'l': {'i': ['adj. 假设的；假想的']}}]}]}]},
    'blng_sents_part': {'sentence-pair': [{'sentence-eng': 'A <b>hypothetical</b> scenario.',
                                        'sentence-translation': '一种假设的情景。'}]},
}


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.environment = patch.dict(os.environ, {'XDG_CACHE_HOME': self.directory.name})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.directory.cleanup()

    def test_youdao_ipa_chinese_and_clean_bilingual_example(self):
        rows = knowledge._parse_youdao(YOUDAO, 'hypothetical')
        self.assertIn('/ˌhaɪpəˈθetɪkəl/', rows[0].title)
        self.assertTrue(any('假设的' in row.title for row in rows))
        example = next(row for row in rows if row.title == 'A hypothetical scenario.')
        self.assertEqual(example.target, 'A hypothetical scenario.\n一种假设的情景。')
        self.assertEqual(rows[-1].kind, 'url')

    def test_english_api_fallback_has_ipa_and_example(self):
        fixture = [{'phonetic': '/test/', 'meanings': [{'partOfSpeech': 'noun', 'definitions': [
            {'definition': 'A procedure.', 'example': 'Run the test.'}]}]}]
        rows = knowledge._parse_dictionaryapi(fixture, 'test')
        self.assertIn('/test/', rows[0].title)
        self.assertTrue(any(row.target == 'Run the test.' for row in rows))
        self.assertEqual(rows[-1].target, 'https://en.wiktionary.org/wiki/test')

    def test_different_headword_is_not_presented_as_requested_word(self):
        fixture = {'ec': {'word': [{'return-phrase': {'l': {'i': 'other'}}}]}}
        self.assertEqual(knowledge._parse_youdao(fixture, 'test'), [])

    def test_http_response_is_bounded(self):
        class Oversized:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read1(self, size):
                return b' ' * 65536
        with patch.object(knowledge.urllib.request, 'urlopen', return_value=Oversized()):
            with self.assertRaises(ValueError):
                knowledge._fetch_json('https://dict.youdao.com/test', time.monotonic() + 1, None)

    def test_private_cache_prevents_repeat_network_request(self):
        with patch.object(knowledge, '_fetch_json', return_value=YOUDAO) as fetch:
            original = knowledge.lookup_word('hypothetical')
            cached = knowledge.lookup_word('hypothetical')
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(original, cached)
        path = knowledge._cache_path('hypothetical')
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_network_failure_falls_back_without_fabricating_unknown_words(self):
        with patch.object(knowledge, '_fetch_json', side_effect=OSError('offline')):
            known = knowledge.lookup_word('reliable')
            unknown = knowledge.lookup_word('notarealwordfortest')
        self.assertIn('/rɪˈlaɪəbəl/', known[0].title)
        self.assertEqual(unknown[0].kind, 'error')
        self.assertEqual(unknown[-1].kind, 'url')

    def test_cancelled_and_invalid_requests_never_reach_network(self):
        cancel = threading.Event()
        cancel.set()
        with patch.object(knowledge, '_fetch_json') as fetch:
            self.assertEqual(knowledge.lookup_word('hypothetical', cancel), [])
            self.assertEqual(knowledge.lookup_word('../../etc/passwd')[0].kind, 'error')
            self.assertEqual(knowledge.lookup_word('')[0].kind, 'error')
            fetch.assert_not_called()

    def test_stale_cache_is_used_if_services_are_unavailable(self):
        rows = knowledge._parse_youdao(YOUDAO, 'hypothetical')
        knowledge._write_cache('hypothetical', rows)
        path = knowledge._cache_path('hypothetical')
        payload = json.loads(path.read_text())
        payload['timestamp'] = 0
        path.write_text(json.dumps(payload))
        with patch.object(knowledge, '_fetch_json', side_effect=OSError('offline')):
            self.assertEqual(knowledge.lookup_word('hypothetical'), rows)


if __name__ == '__main__':
    unittest.main()
