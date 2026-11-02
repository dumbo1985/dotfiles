"""Behavior checks for arithmetic safety and literal, bounded filename lookup."""
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
from launcher_search import Result, calculate, search_applications, search_files


class CalculatorTests(unittest.TestCase):
    def test_arithmetic_and_scientific_input(self):
        cases = {'2+3*4': '14', '(2+3)*4': '20', '2^8': '256',
                 '12×3÷2': '18', '−2+3': '1', '200*10%': '20',
                 '100+20%': '100.2', '(100+20)%': '1.2', '10%3': '1',
                 'sqrt(4)%': '0.02', '1e-3%': '1e-05', '2^10%': '1.07177346253629',
                 '=sqrt(81)': '9', 'round(pi, 2)': '3.14',
                 '0.1+0.2': '0.3', '1e3+2': '1002', 'ln(e)': '1'}
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                result = calculate(expression)
                self.assertEqual(result.kind, 'calculator')
                self.assertEqual(result.target, expected)

    def test_plain_search_is_not_a_calculation(self):
        for query in ('firefox', '2026-report.pdf', 'README.md', 'invoice 2026'):
            self.assertIsNone(calculate(query))

    def test_invalid_and_dangerous_input_never_executes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'must-not-exist'
            expressions = [f"=__import__('pathlib').Path({str(target)!r}).touch()",
                           '=(1).__class__', '=[1]*1000000000', '=True+2',
                           '=2**999999999', '=9**9**9', '=1/0', '=sqrt(-1)', '=exp(1000)']
            start = time.monotonic()
            for expression in expressions:
                with self.subTest(expression=expression):
                    self.assertEqual(calculate(expression).kind, 'error')
            self.assertFalse(target.exists())
            self.assertLess(time.monotonic() - start, 1)


class FileSearchTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.home = Path(self.temporary.name)
        (self.home / 'projects').mkdir()
        (self.home / 'projects' / 'Plan[1].TXT').write_text('example')
        (self.home / 'projects' / 'plan11.txt').write_text('example')
        for excluded in ('node_modules', '.cache', 'build'):
            (self.home / excluded).mkdir()
            (self.home / excluded / 'Plan[1].TXT').write_text('ignored')

    def tearDown(self):
        self.temporary.cleanup()

    def test_literal_case_insensitive_lookup_and_exclusions(self):
        results = search_files('plan[1]', home=self.home)
        self.assertEqual([result.target for result in results], [str(self.home / 'projects' / 'Plan[1].TXT')])
        self.assertEqual(results[0].kind, 'file')

    def test_explicit_path_spaces_and_browsing(self):
        path = self.home / 'space name.txt'
        path.write_text('example')
        self.assertEqual(search_files('~/space name.txt', home=self.home)[0].target, str(path))
        results = search_files('~/projects/', home=self.home)
        self.assertEqual({result.title for result in results}, {'Plan[1].TXT', 'plan11.txt'})
        self.assertEqual(search_files('~', home=self.home)[0].target, str(self.home))

    def test_dependency_caches_excluded_without_hiding_user_pkg_projects(self):
        for relative in ('go/pkg/mod/library', 'go/pkg/sumdb/server', 'Applications/editor/squashfs-root/usr', 'pkg/project'):
            path = self.home / relative / 'README.md'
            path.parent.mkdir(parents=True)
            path.write_text('example')
        expected = [str(self.home / 'pkg/project/README.md')]
        self.assertEqual([result.target for result in search_files('README', home=self.home)], expected)
        with patch('launcher_search.shutil.which', return_value=None):
            self.assertEqual([result.target for result in search_files('README', home=self.home)], expected)

    def test_shallow_matches_prioritized_before_result_cap(self):
        (self.home / 'notes.txt').write_text('personal')
        source = self.home / 'source/deep/library/docs'
        source.mkdir(parents=True)
        for index in range(20):
            (source / f'notes-{index}.txt').write_text('library')
        for fallback in (False, True):
            with self.subTest(fallback=fallback):
                if fallback:
                    with patch('launcher_search.shutil.which', return_value=None):
                        results = search_files('notes', limit=1, home=self.home)
                else:
                    results = search_files('notes', limit=1, home=self.home)
                self.assertEqual([result.target for result in results], [str(self.home / 'notes.txt')])

    def test_relative_path_fragments_remain_literal(self):
        expected = [str(self.home / 'projects/Plan[1].TXT')]
        self.assertEqual([result.target for result in search_files('projects/plan[1]', home=self.home)], expected)
        with patch('launcher_search.shutil.which', return_value=None):
            self.assertEqual([result.target for result in search_files('projects/plan[1]', home=self.home)], expected)

    def test_cancel_and_limit(self):
        cancel = threading.Event()
        cancel.set()
        self.assertEqual(search_files('plan', cancel=cancel, home=self.home), [])
        self.assertLessEqual(len(search_files('plan', limit=1, home=self.home)), 1)
        self.assertEqual(search_files('p', home=self.home), [])

    def test_running_search_is_cancelled_and_child_is_reaped(self):
        original_popen = subprocess.Popen
        children = []
        def slow_search(*args, **kwargs):
            child = original_popen([sys.executable, '-c', 'import time; time.sleep(30)'], **kwargs)
            children.append(child)
            return child
        cancel = threading.Event()
        timer = threading.Timer(.05, cancel.set)
        start = time.monotonic()
        timer.start()
        try:
            with patch('launcher_search.subprocess.Popen', side_effect=slow_search):
                self.assertEqual(search_files('plan', cancel=cancel, home=self.home), [])
        finally:
            timer.cancel()
        self.assertLess(time.monotonic() - start, 1)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].returncode)

    def test_application_search_keeps_types_and_prioritizes_names(self):
        apps = [Result('Editor', 'Edit files', 'application', 'editor.desktop'),
                Result('Other app', 'Launch editor', 'application', 'other.desktop')]
        self.assertEqual(search_applications('editor', apps)[0].target, 'editor.desktop')
        self.assertEqual(search_applications('EDIT FILE', apps), apps[:1])


if __name__ == '__main__':
    unittest.main()
