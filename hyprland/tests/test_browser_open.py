"""External-link focus decisions without opening Chrome or changing desktop focus."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import browser_open as browser


def window(address='0x10', app='google-chrome', history=0, title='Page', **changes):
    client = {'address': address, 'class': app, 'initialClass': app,
              'mapped': True, 'hidden': False, 'focusHistoryID': history,
              'title': title, 'workspace': {'id': 1, 'name': '1'}}
    client.update(changes)
    return client


class BrowserWindowTests(unittest.TestCase):
    def test_only_mapped_normal_chrome_windows_are_candidates(self):
        good = window('0x20', history=8)
        pwa = window('0x30')
        pwa['initialClass'] = 'chrome-example-Default'
        invalid = [None, 'invalid', window(address='0x1);bad()'),
                   window(address=7), window(address='0x10\n'),
                   window(hidden=True), window(mapped=False), window(app=''),
                   window(app='google-chrome-helper'), window(app='firefox'), pwa,
                   window(app='chrome-example-Default', initialClass='google-chrome')]
        self.assertEqual(browser.chrome_clients([*invalid, good]), [good])

    def test_new_window_wins_over_title_change_and_recent_window(self):
        recent = window('0x10', history=0)
        changed = window('0x20', history=3)
        new = window('0x30', history=7)
        target = browser.choose_target([recent, changed],
                                       [recent, dict(changed, title='New page'), new])
        self.assertEqual(target['address'], new['address'])

    def test_changed_title_identifies_the_receiving_window(self):
        recent = window('0x10', history=0)
        receiving = window('0x20', history=4)
        target = browser.choose_target([recent, receiving],
                                       [recent, dict(receiving, title='Opened link')])
        self.assertEqual(target['address'], receiving['address'])

    def test_mru_fallback_ignores_unknown_history(self):
        recent = window('0x10', history=1)
        older = window('0x20', history=6)
        unknown = window('0x30', history=-1)
        clients = [unknown, older, recent]
        self.assertEqual(browser.choose_target(clients, clients)['address'], recent['address'])

    def test_target_follows_the_window_to_any_workspace(self):
        original = window()
        for name in ('3', '7', '10', 'special:browser'):
            with self.subTest(workspace=name):
                moved = dict(original, workspace={'name': name})
                target = browser.choose_target([original], [moved])
                self.assertEqual(target['address'], original['address'])
                self.assertEqual(target['workspace']['name'], name)

    def test_no_chrome_window_has_no_focus_target(self):
        self.assertIsNone(browser.choose_target([], [window(app='OtherApp')]))


class BrowserLaunchTests(unittest.TestCase):
    def test_http_arguments_reach_chrome_unchanged_without_shell(self):
        arguments = ['https://example.invalid/?a=1&b=two words',
                     'https://example.invalid/\"quoted\"', '--profile-directory=Profile 1']
        process = Mock()
        process.poll.return_value = 0
        client = window()
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test'}, clear=True), \
                patch.object(browser, 'query_clients', return_value=[client]), \
                patch.object(browser, 'focus_window') as focus, \
                patch.object(browser.subprocess, 'Popen', return_value=process) as launch, \
                patch.object(browser.time, 'sleep'), \
                patch.object(browser.time, 'monotonic', side_effect=[0, 0, 0, .5]):
            self.assertEqual(browser.open_browser(arguments), 0)
            self.assertEqual(launch.call_args.args[0], [browser.CHROME, *arguments])
            self.assertFalse(launch.call_args.kwargs.get('shell', False))
            focus.assert_called_once_with(client['address'])

    def test_non_web_launches_never_query_or_focus_windows(self):
        for arguments in ([], ['--new-window'], ['file:///tmp/document.html']):
            with self.subTest(arguments=arguments), \
                    patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test'}, clear=True), \
                    patch.object(browser, 'query_clients') as query, \
                    patch.object(browser, 'focus_window') as focus, \
                    patch.object(browser.subprocess, 'Popen') as launch:
                self.assertEqual(browser.open_browser(arguments), 0)
                launch.assert_called_once()
                query.assert_not_called()
                focus.assert_not_called()

    def test_other_desktop_sessions_only_launch_chrome(self):
        with patch.dict(os.environ, {}, clear=True), \
                patch.object(browser, 'query_clients') as query, \
                patch.object(browser, 'focus_window') as focus, \
                patch.object(browser.subprocess, 'Popen') as launch:
            self.assertEqual(browser.open_browser(['https://example.invalid/']), 0)
            launch.assert_called_once()
            query.assert_not_called()
            focus.assert_not_called()

    def test_unavailable_compositor_does_not_prevent_opening_the_link(self):
        process = Mock()
        process.poll.return_value = 0
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test'}, clear=True), \
                patch.object(browser, 'query_clients', side_effect=OSError('no compositor')), \
                patch.object(browser, 'focus_window') as focus, \
                patch.object(browser.subprocess, 'Popen', return_value=process) as launch, \
                patch.object(browser.time, 'sleep'):
            self.assertEqual(browser.open_browser(['https://example.invalid/']), 0)
            launch.assert_called_once()
            focus.assert_not_called()

    def test_cold_start_waits_for_a_mapped_window(self):
        process = Mock()
        process.poll.return_value = None
        client = window(workspace={'id': 7, 'name': '7'})
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test'}, clear=True), \
                patch.object(browser, 'query_clients', side_effect=[[], [], [client]]), \
                patch.object(browser, 'focus_window') as focus, \
                patch.object(browser.subprocess, 'Popen', return_value=process), \
                patch.object(browser.time, 'sleep'), \
                patch.object(browser.time, 'monotonic', return_value=0):
            self.assertEqual(browser.open_browser(['https://example.invalid/']), 0)
            focus.assert_called_once_with(client['address'])

    def test_no_window_cold_start_has_a_bounded_wait(self):
        process = Mock()
        process.poll.return_value = None
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE': 'test'}, clear=True), \
                patch.object(browser, 'query_clients', return_value=[]) as query, \
                patch.object(browser, 'focus_window') as focus, \
                patch.object(browser.subprocess, 'Popen', return_value=process), \
                patch.object(browser.time, 'sleep'), \
                patch.object(browser.time, 'monotonic', side_effect=[0, 0, *range(9)]):
            self.assertEqual(browser.open_browser(['https://example.invalid/']), 0)
            self.assertLessEqual(query.call_count, 9)
            focus.assert_not_called()


class BrowserDesktopEntryTests(unittest.TestCase):
    def test_install_preserves_chrome_identity_and_native_actions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'original.desktop'
            source.write_text('[Desktop Entry]\nName=Google Chrome\n'
                              'Exec=/usr/bin/google-chrome-stable %U\n'
                              'StartupWMClass=google-chrome\nMimeType=x-scheme-handler/https;\n'
                              '[Desktop Action new-window]\nExec=/usr/bin/google-chrome-stable\n'
                              '[Desktop Action new-private-window]\n'
                              'Exec=/usr/bin/google-chrome-stable --incognito\n')
            self.assertTrue(browser.install_desktop_entry(root / 'config', root / 'data', source))
            target = root / 'data/applications/google-chrome.desktop'
            installed = target.read_text()
            self.assertIn('Name=Google Chrome\n', installed)
            self.assertIn('StartupWMClass=google-chrome\n', installed)
            self.assertIn('MimeType=x-scheme-handler/https;\n', installed)
            self.assertIn('[Desktop Action new-window]\nExec=/usr/bin/google-chrome-stable\n', installed)
            self.assertIn('Exec=/usr/bin/google-chrome-stable --incognito\n', installed)
            self.assertIn('bin/browser-open', installed.split('[Desktop Action')[0])
            self.assertTrue(browser.install_desktop_entry(root / 'config', root / 'data', source))
            self.assertEqual(target.read_text(), installed)

    def test_existing_user_override_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'original.desktop'
            source.write_text('[Desktop Entry]\nExec=original\n')
            target = root / 'data/applications/google-chrome.desktop'
            target.parent.mkdir(parents=True)
            custom = '[Desktop Entry]\nExec=user-custom-browser\n'
            target.write_text(custom)
            self.assertFalse(browser.install_desktop_entry(root / 'config', root / 'data', source))
            self.assertEqual(target.read_text(), custom)


if __name__ == '__main__':
    unittest.main()
