"""Feature routing, discoverability and action boundary checks."""
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
from launcher_search import Result
from launcher_features import (background_results, help_results, initial_results,
                               parse_query, run_system_action, website)


class RoutingTests(unittest.TestCase):
    def test_prefixes_are_complete_tokens_and_empty_modes_are_available(self):
        for text, mode in [('w neovide', 'windows'), ('v', 'clipboard'), ('p ', 'projects'),
                           ('t workspace', 'tmux'), ('s 日期', 'snippets'), ('dict hypothetical', 'dictionary'),
                           ('g hyprland 快捷键', 'google'), ('b 搜索', 'bing'), ('sys', 'system'),
                           ('>锁屏', 'system'), ('?', 'help')]:
            with self.subTest(text=text):
                self.assertEqual(parse_query(text).mode, mode)
        for text in ('github.com', 'git', 'g++', 'pavucontrol', 'v1.py', 'dictation.txt'):
            self.assertEqual(parse_query(text).mode, 'normal')

    def test_help_rows_only_fill_input_and_never_execute_actions(self):
        choices = help_results()
        self.assertGreaterEqual(len(choices), 10)
        self.assertTrue(all(result.kind == 'fill' for result in choices))
        self.assertEqual(initial_results(parse_query(''), [])[0].target, '?')

    def test_websites_and_filenames_are_distinguished(self):
        self.assertEqual(website('github.com'), 'https://github.com')
        self.assertEqual(website('https://example.com/a?q=x'), 'https://example.com/a?q=x')
        self.assertEqual(website('localhost:8080'), 'http://localhost:8080')
        self.assertEqual(website('192.168.1.1'), 'http://192.168.1.1')
        for text in ('README.md', 'main.ts', 'main.js', 'index.html', 'foo.css', 'file.json',
                     'javascript:alert(1)', 'ftp://example.com', 'https://user:pass@example.com',
                     'https://example.com:99999', 'https://'):
            self.assertIsNone(website(text), text)

    def test_google_url_encodes_text_and_does_not_execute_it(self):
        results = initial_results(parse_query('g linux & wayland $(hello)'), [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].kind, 'url')
        self.assertIn('linux+%26+wayland+%24%28hello%29', results[0].target)

    def test_unit_conversion_precedes_arithmetic_and_system_actions_are_explicit(self):
        results = initial_results(parse_query('10 km to mile'), [])
        self.assertEqual(results[0].kind, 'conversion')
        self.assertEqual(initial_results(parse_query('12*34'), [])[0].target, '408')
        self.assertEqual(initial_results(parse_query('锁屏'), [])[0].target, 'lock')
        self.assertFalse(any(row.target == 'lock' for row in initial_results(parse_query(''), [])))

    def test_cancelled_search_does_not_call_provider(self):
        cancel = threading.Event()
        cancel.set()
        with patch('launcher_context.search_windows') as search:
            self.assertEqual(background_results(parse_query('w neovide'), cancel), [])
            search.assert_not_called()

    def test_feature_modes_dispatch_without_plain_file_search(self):
        expected = Result('Window', 'Title', 'window', '0x123')
        with patch('launcher_context.search_windows', return_value=[expected]) as search:
            self.assertEqual(background_results(parse_query('w neovide')), [expected])
            self.assertEqual(search.call_args.args[0], 'neovide')
        with patch('launcher_context.search_clipboard', return_value=[]) as search:
            self.assertEqual(background_results(parse_query('v')), [])
            search.assert_called_once()

    def test_system_actions_use_fixed_argv_and_reject_unknown_commands(self):
        with patch('launcher_features.subprocess.Popen') as launch:
            run_system_action('screenshot')
            arguments = launch.call_args.args[0]
            self.assertTrue(arguments[0].endswith('/bin/screenshot'))
            self.assertEqual(arguments[1:], ['menu'])
            self.assertNotIn('shell', launch.call_args.kwargs)
            with self.assertRaises(ValueError):
                run_system_action('lock; rm -rf /')
            self.assertEqual(launch.call_count, 1)

    def test_ocr_and_layout_actions_use_existing_helpers(self):
        for text, key, suffix in [('识字', 'ocr', ['screen-ocr']),
                                  ('保存窗口布局', 'layout-save', ['window-layout', '--save']),
                                  ('恢复窗口布局', 'layout-restore', ['window-layout', '--restore'])]:
            choices = initial_results(parse_query(text), [])
            self.assertTrue(any(result.kind == 'system' and result.target == key for result in choices))
            with patch('launcher_features.subprocess.Popen') as launch:
                run_system_action(key)
                command = launch.call_args.args[0]
                self.assertTrue(command[0].endswith('/bin/' + suffix[0]))
                self.assertEqual(command[1:], suffix[1:])


if __name__ == '__main__':
    unittest.main()
