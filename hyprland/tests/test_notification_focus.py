"""Offline notification-to-window matching, with no desktop focus changes."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import notification_focus as focus


def window(address='0x10', app='Bytedance-feishu', history=0, **overrides):
    return dict(address=address, **{'class': app}, initialClass=app,
                focusHistoryID=history, **overrides)


class NotificationFocusTests(unittest.TestCase):
    def test_feishu_chinese_and_desktop_entry_match_existing_window(self):
        client = window()
        for app_name, desktop_entry in (('飞书', ''), ('Feishu', ''),
                                         ('', 'bytedance-feishu.desktop'),
                                         ('飞书', 'bytedance-feishu')):
            with self.subTest(app_name=app_name, desktop_entry=desktop_entry):
                scores = focus.app_identities(app_name, desktop_entry, directories=[])
                self.assertIs(focus.choose_client([client], scores), client)

    def test_desktop_file_connects_localized_name_and_startup_class(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'org.example.Messenger.desktop').write_text(
                '[Desktop Entry]\nType=Application\nName=Example Messenger\n'
                'Name[zh_CN]=示例通讯\nStartupWMClass=ExampleMessengerWindow\n',
                encoding='utf-8')
            client = window(app='ExampleMessengerWindow')
            for name, entry in (('示例通讯', ''), ('', 'org.example.Messenger.desktop')):
                with self.subTest(name=name, entry=entry):
                    scores = focus.app_identities(name, entry, directories=[directory])
                    self.assertIs(focus.choose_client([client], scores), client)

    def test_most_recent_matching_window_wins(self):
        older = window('0x11', history=7)
        recent = window('0x12', history=1)
        unknown_history = window('0x13', history=-1)
        scores = focus.app_identities('飞书', directories=[])
        self.assertIs(focus.choose_client([older, unknown_history, recent], scores), recent)

    def test_target_tracks_window_after_it_moves_to_another_workspace(self):
        scores = focus.app_identities('飞书', directories=[])
        for workspace in (1, 7, 10, 'special:chat'):
            client = window(workspace={'name': str(workspace)})
            selected = focus.choose_client([client], scores)
            self.assertIs(selected, client)
            self.assertEqual(selected['workspace']['name'], str(workspace))

    def test_desktop_entry_identity_precedes_app_name_match(self):
        by_name = window('0x11', app='Other Messenger', history=0)
        by_entry = window('0x12', history=5)
        scores = focus.app_identities('Other Messenger', 'bytedance-feishu', directories=[])
        self.assertIs(focus.choose_client([by_name, by_entry], scores), by_entry)

    def test_invalid_hidden_unmapped_and_classless_windows_are_ignored(self):
        good = window('0x20', history=8)
        invalid = [window(address='0x1);malicious()'), window(address=10),
                   window(address='0x10\n'), window(hidden=True),
                   window(mapped=False), window(app=''), None, 'invalid']
        scores = focus.app_identities('飞书', directories=[])
        self.assertIs(focus.choose_client([*invalid, good], scores), good)

    def test_initial_class_can_match_after_runtime_class_change(self):
        client = window(app='Transient Dialog')
        client['initialClass'] = 'Bytedance-feishu'
        scores = focus.app_identities('飞书', directories=[])
        self.assertIs(focus.choose_client([client], scores), client)

    def test_complete_identity_match_never_uses_title_or_substring(self):
        scores = focus.app_identities('飞书', directories=[])
        clients = [window(app='Bytedance-feishu-helper'),
                   window(app='OtherApp', title='飞书'),
                   window(app='NotFeishu'), window(app='FeishuPreview')]
        self.assertIsNone(focus.choose_client(clients, scores))

    def test_unmatched_notification_does_not_close_panel_or_focus(self):
        result = subprocess.CompletedProcess([], 0, json.dumps([window()]), '')
        with patch.dict(focus.os.environ, {'SWAYNC_APP_NAME': 'UnknownApplication',
                                         'SWAYNC_DESKTOP_ENTRY': ''}), \
                patch.object(focus, 'desktop_directories', return_value=[]), \
                patch.object(focus, 'command', return_value=result) as command, \
                patch.object(focus, 'activate') as activate, \
                patch.object(focus.time, 'sleep'):
            self.assertEqual(focus.main([]), 0)
            command.assert_called_once_with(['hyprctl', 'clients', '-j'])
            activate.assert_not_called()

    def test_notification_without_app_identity_is_a_noop(self):
        with patch.dict(focus.os.environ, {'SWAYNC_APP_NAME': '',
                                         'SWAYNC_DESKTOP_ENTRY': ''}), \
                patch.object(focus, 'command') as command, \
                patch.object(focus, 'activate') as activate:
            self.assertEqual(focus.main([]), 0)
            command.assert_not_called()
            activate.assert_not_called()

    def test_dry_run_reports_target_without_changing_focus(self):
        client = window(workspace={'id': 3, 'name': '3'})
        result = subprocess.CompletedProcess([], 0, json.dumps([client]), '')
        output = io.StringIO()
        with patch.dict(focus.os.environ, {'SWAYNC_APP_NAME': '飞书',
                                         'SWAYNC_DESKTOP_ENTRY': ''}), \
                patch.object(focus, 'desktop_directories', return_value=[]), \
                patch.object(focus, 'command', return_value=result), \
                patch.object(focus, 'activate') as activate, redirect_stdout(output):
            self.assertEqual(focus.main(['--dry-run']), 0)
            self.assertEqual(json.loads(output.getvalue())['address'], client['address'])
            activate.assert_not_called()


if __name__ == '__main__':
    unittest.main()
