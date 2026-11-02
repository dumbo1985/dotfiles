"""Context providers/actions tested with local fixtures and mocked external actions."""
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import launcher_context as context


class CommandTests(unittest.TestCase):
    def test_cancellation_terminates_and_reaps_reader_process(self):
        original = subprocess.Popen
        children = []
        def track(*args, **kwargs):
            process = original(*args, **kwargs)
            children.append(process)
            return process
        cancel = threading.Event()
        timer = threading.Timer(.05, cancel.set)
        timer.start()
        start = time.monotonic()
        try:
            with patch.object(context.subprocess, 'Popen', side_effect=track):
                output = context._command_bytes([sys.executable, '-c', 'import time; time.sleep(30)'], cancel)
        finally:
            timer.cancel()
        self.assertEqual(output, b'')
        self.assertLess(time.monotonic() - start, 1)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].returncode)


class WindowTests(unittest.TestCase):
    def test_window_filter_and_focus_address_validation(self):
        clients = [dict(address='0x123', title='main.py — Neovide', **{'class': 'neovide'},
                        workspace={'id': 2}, focusHistoryID=0),
                   dict(address='0x456', title='hidden', mapped=False),
                   dict(address='bad; dangerous', title='invalid'), None]
        with patch.object(context, '_text', return_value=json.dumps(clients)):
            results = context.search_windows('neovide 2')
        self.assertEqual([result.target for result in results], ['0x123'])
        with patch.object(context.subprocess, 'run') as run:
            with self.assertRaises(ValueError):
                context.activate_window('0x123);os.execute("bad")')
            run.assert_not_called()
            context.activate_window('0x123')
            command = run.call_args.args[0]
            self.assertEqual(command[:2], ['hyprctl', 'eval'])
            self.assertIn('"address:0x123"', command[2])


class ClipboardTests(unittest.TestCase):
    def test_ids_and_binary_rows_preserved_without_decoding(self):
        output = '12\tText containing an extra\ttab\n13\t[[ binary data 1 KiB png 10x10 ]]\ninvalid row\n'
        with patch.object(context, '_program', return_value='/mock/cliphist'), patch.object(context, '_text', return_value=output):
            results = context.search_clipboard('')
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].target, '12\tText containing an extra\ttab')
        self.assertEqual(results[1].icon, 'image-x-generic')

    def test_decode_pipes_binary_to_wl_copy_with_mime(self):
        decoder, copier = MagicMock(), MagicMock()
        decoder.stdin, decoder.stdout = io.BytesIO(), io.BytesIO()
        decoder.returncode = copier.returncode = 0
        with patch.object(context, '_program', side_effect=lambda name: '/mock/' + name), \
                patch.object(context.subprocess, 'Popen', side_effect=[decoder, copier]) as popen:
            context.copy_clipboard('13\t[[ binary data 1 KiB png 10x10 ]]')
        self.assertEqual(popen.call_args_list[0].args[0], ['/mock/cliphist', 'decode'])
        self.assertEqual(popen.call_args_list[1].args[0], ['/mock/wl-copy', '--type', 'image/png'])
        self.assertIs(popen.call_args_list[1].kwargs['stdin'], decoder.stdout)
        self.assertTrue(decoder.stdin.closed)
        decoder.wait.assert_called_once_with(timeout=3)
        copier.wait.assert_called_once_with(timeout=3)


class ProjectAndSnippetTests(unittest.TestCase):
    def test_projects_find_git_worktrees_and_manifests_skip_dependencies(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            root = home / 'Projects'
            for relative, marker in [('repo', '.git'), ('space project', 'pyproject.toml'),
                                     ('nested/worktree', '.git'), ('repo/node_modules/ignored', 'package.json')]:
                path = root / relative
                path.mkdir(parents=True)
                (path / marker).touch()
            with patch.object(context, 'PROJECTS_FILE', home / 'missing.json'):
                results = context.load_projects(home=home)
            self.assertEqual({result.title for result in results}, {'repo', 'space project', 'worktree'})
            self.assertEqual(context.search_projects('space', projects=results)[0].title, 'space project')
            cancel = threading.Event()
            cancel.set()
            self.assertEqual(context.load_projects(cancel, home), [])

    def test_open_project_uses_cwd_and_argv(self):
        with tempfile.TemporaryDirectory(prefix='project space ') as directory:
            with patch.object(context, '_program', return_value='/mock/neovide'), patch.object(context.subprocess, 'Popen') as popen:
                context.open_project(directory)
            self.assertEqual(popen.call_args.args[0], ['/mock/neovide', '--', '.'])
            self.assertEqual(popen.call_args.kwargs['cwd'], directory)
            self.assertNotIn('shell', popen.call_args.kwargs)

    def test_project_dependencies_not_listed_as_projects(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            root = home / 'Projects/repo'
            library = root / 'examples/sample'
            library.mkdir(parents=True)
            (root / '.git').touch()
            (library / 'CMakeLists.txt').touch()
            with patch.object(context, 'PROJECTS_FILE', home / 'missing.json'):
                self.assertEqual([result.title for result in context.load_projects(home=home)], ['repo'])

    def test_snippet_expansion_and_missing_email_configuration(self):
        now = datetime(2026, 10, 30, 13, 14, 15)
        fixtures = [{'name': '日期', 'content': '{{date}} {{time}} {{year}}', 'keywords': ['date']},
                    {'name': '邮箱', 'content': ''}]
        with patch.object(context, 'load_snippets', return_value=fixtures), \
                patch.object(context, 'datetime') as clock, patch.object(context, '_text', return_value=''):
            clock.now.return_value = now
            self.assertEqual(context.search_snippets('date')[0].target, '2026-10-30 13:14:15 2026')
            self.assertEqual(context.search_snippets('邮箱')[0].kind, 'file')


class TmuxTests(unittest.TestCase):
    def test_existing_session_is_not_duplicated_and_new_names_are_validated(self):
        with patch.object(context, '_program', return_value='/mock/tmux'), \
                patch.object(context, '_text', return_value='workspace\t3\t1\nresearch\t1\t0\n'):
            results = context.search_tmux('workspace')
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].title, 'workspace')
            self.assertEqual(context.search_tmux('new-work')[0].target, 'new-work')
            self.assertEqual(context.search_tmux('bad;touch /tmp/file'), [])

    def test_open_tmux_uses_attach_or_create_and_no_shell(self):
        def executable(name):
            return {'tmux': '/usr/bin/tmux', 'kitty': '/usr/bin/kitty'}.get(name)
        with patch.object(context, '_program', side_effect=executable), \
                patch.dict(os.environ, {'TMUX': 'old-session', 'DOTFILES_LAUNCHER_TERMINAL': ''}), \
                patch.object(context.subprocess, 'Popen') as popen:
            context.open_tmux('workspace')
        self.assertEqual(popen.call_args.args[0], ['/usr/bin/kitty', '--', '/usr/bin/tmux', 'new-session', '-A', '-s', 'workspace'])
        self.assertNotIn('TMUX', popen.call_args.kwargs['env'])
        self.assertNotIn('shell', popen.call_args.kwargs)


if __name__ == '__main__':
    unittest.main()
