"""Cycle/layout behavior without moving or focusing any real desktop window."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import window_memory as memory


def window(address, app='neovide', title='', workspace=1, monitor=0, floating=False, history=0):
    return {'address': address, 'class': app, 'initialClass': app, 'title': title,
            'workspace': {'id': workspace, 'name': str(workspace)}, 'monitor': monitor,
            'floating': floating, 'at': [20, 80], 'size': [800, 600], 'focusHistoryID': history}


MONITORS = [dict(id=0, name='DP-1', width=3840, height=2160, scale=1.25, transform=0, x=0, y=0),
            dict(id=1, name='DP-2', width=3840, height=2160, scale=1.25, transform=1, x=3072, y=0)]


class CycleTests(unittest.TestCase):
    def test_app_aliases_keep_pwa_distinct_and_exclude_preview(self):
        self.assertEqual(memory.app_key(window('0x1', 'org.wezfurlong.wezterm')), 'wezterm')
        self.assertEqual(memory.app_key(window('0x2', 'WezTerm')), 'wezterm')
        browser = window('0x3', 'google-chrome')
        pwa = dict(browser, initialClass='chrome-test-app-Default')
        self.assertNotEqual(memory.app_key(browser), memory.app_key(pwa))
        self.assertEqual(memory.visible_clients([window('0x4', 'org.gnome.NautilusPreviewer')]), [])

    def test_repeated_app_cycle_freezes_mru_instead_of_pingpong(self):
        clients = [window('0x1', 'editor', history=0), window('0x2', 'browser', history=1),
                   window('0x3', 'terminal', history=2), window('0x4', 'editor', history=3)]
        first, state = memory.plan_cycle(clients, '0x1', now=10)
        self.assertEqual(first['target'], '0x2')
        reordered = [dict(client, focusHistoryID={'0x2': 0, '0x1': 1, '0x3': 2, '0x4': 3}[client['address']]) for client in clients]
        second, state = memory.plan_cycle(reordered, '0x2', state, now=10.2)
        self.assertEqual(second['target'], '0x3')
        third, _ = memory.plan_cycle(reordered, '0x3', state, now=10.4)
        self.assertEqual(third['target'], '0x1')

    def test_same_app_reverse_and_external_focus_reset(self):
        clients = [window('0x1', history=0), window('0x2', history=1), window('0x3', history=2),
                   window('0x4', 'browser', history=3)]
        plan, state = memory.plan_cycle(clients, '0x1', same_app=True, reverse=True, now=1)
        self.assertEqual(plan['target'], '0x3')
        plan, _ = memory.plan_cycle(clients, '0x2', state, same_app=True, now=1.1)
        self.assertEqual(plan['target'], '0x3')
        plan, _ = memory.plan_cycle(clients, '0x1', {}, now=5)
        self.assertEqual(plan['count'], 2)


class GeometryTests(unittest.TestCase):
    def test_portrait_logical_bounds_and_clamp(self):
        self.assertEqual(memory.monitor_bounds(MONITORS[1]), (3072, 0, 1728, 3072))
        client = window('0x1')
        record = memory.placement(client, MONITORS)
        record.update(monitor='DP-2', workspace=9, floating=True,
                      geometry={'x': 99999, 'y': -20, 'width': 5000, 'height': 5000})
        plan = memory.restore_plan(client, record, MONITORS)
        self.assertEqual(plan['geometry'], {'x': 3080, 'y': 8, 'width': 1712, 'height': 3056})
        self.assertTrue(any(step['dispatcher'] == 'window.resize' for step in plan['steps']))

    def test_tiled_restore_never_forces_geometry(self):
        client = window('0x1')
        record = memory.placement(client, MONITORS)
        record.update(monitor='DP-2', workspace=9)
        plan = memory.restore_plan(client, record, MONITORS)
        self.assertIsNone(plan['geometry'])
        self.assertEqual([step['dispatcher'] for step in plan['steps']], ['window.move', 'workspace.move'])
        self.assertIsNone(memory.restore_plan(client, record, MONITORS[:1]))
        record.update(monitor='DP-1', workspace=3)
        plan = memory.restore_plan(client, record, MONITORS)
        self.assertEqual([step['dispatcher'] for step in plan['steps']], ['window.move', 'workspace.move'])


class LayoutTests(unittest.TestCase):
    def test_baseline_learns_without_plans_and_tracks_manual_moves(self):
        tracker = memory.LayoutMemory()
        client = window('0x1', title='project A')
        self.assertEqual(tracker.observe([client], MONITORS, baseline=True, now=1), [])
        self.assertEqual(tracker.document()['windows'][0]['workspace'], 1)
        client = dict(client, workspace={'id': 8, 'name': '8'}, monitor=1)
        self.assertEqual(tracker.observe([client], MONITORS, now=4), [])
        record = tracker.document()['windows'][0]
        self.assertEqual((record['workspace'], record['monitor']), (8, 'DP-2'))

    def test_monitor_unplug_migration_does_not_overwrite_desired_output(self):
        tracker = memory.LayoutMemory()
        original = window('0x1', title='right', workspace=9, monitor=1)
        tracker.observe([original], MONITORS, baseline=True, now=1)
        migrated = dict(original, monitor=0, workspace={'id': 9, 'name': '9'})
        self.assertEqual(tracker.observe([migrated], MONITORS[:1], now=10), [])
        self.assertEqual(tracker.observe([migrated], MONITORS[:1], now=60), [])
        self.assertEqual(tracker.document()['windows'][0]['monitor'], 'DP-2')
        self.assertEqual(tracker.observe([migrated], MONITORS, now=61), [])
        plans = tracker.observe([migrated], MONITORS, now=61.5)
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]['monitor'], 'DP-2')
        self.assertEqual(tracker.document()['windows'][0]['monitor'], 'DP-2')

    def test_new_window_restores_title_match_across_login_and_delays_settle(self):
        old = memory.LayoutMemory()
        first = window('0x1', title='project A', workspace=9, monitor=1)
        second = window('0x2', title='project B', workspace=3)
        old.observe([first, second], MONITORS, baseline=True, now=1)
        tracker = memory.LayoutMemory(old.document())
        tracker.observe([], MONITORS, baseline=True, now=10)
        reopened = window('0x3', title='project A', workspace=1)
        self.assertEqual(tracker.observe([reopened], MONITORS, now=11), [])
        plans = tracker.observe([reopened], MONITORS, now=11.7)
        self.assertEqual(len(plans), 1)
        self.assertEqual((plans[0]['workspace'], plans[0]['monitor']), (9, 'DP-2'))
        tracker.restore_finished('0x3', now=11.7)
        self.assertEqual(tracker.observe([reopened], MONITORS, now=12), [])
        record = next(item for item in tracker.document()['windows'] if item['title'] == 'project A')
        self.assertEqual(record['monitor'], 'DP-2')

    def test_simultaneous_new_windows_keep_stable_per_app_default(self):
        tracker = memory.LayoutMemory()
        original = window('0x1', title='A', workspace=9, monitor=1)
        tracker.observe([original], MONITORS, baseline=True, now=1)
        first_new = window('0x2', title='B', workspace=1)
        second_new = window('0x3', title='C', workspace=2)
        tracker.observe([original, first_new, second_new], MONITORS, now=5)
        plans = tracker.observe([original, first_new, second_new], MONITORS, now=6)
        self.assertEqual(len(plans), 2)
        self.assertEqual({(plan['workspace'], plan['monitor']) for plan in plans}, {(9, 'DP-2')})

    def test_manual_primary_move_updates_default_for_future_windows(self):
        tracker = memory.LayoutMemory()
        original = window('0x1', title='A', workspace=1)
        tracker.observe([original], MONITORS, baseline=True, now=1)
        moved = dict(original, workspace={'id': 9, 'name': '9'}, monitor=1)
        tracker.observe([moved], MONITORS, now=5)
        first_new = window('0x2', title='B', workspace=2)
        second_new = window('0x3', title='C', workspace=3)
        tracker.observe([moved, first_new, second_new], MONITORS, now=6)
        plans = tracker.observe([moved, first_new, second_new], MONITORS, now=7)
        self.assertEqual(len(plans), 2)
        self.assertEqual({(plan['workspace'], plan['monitor']) for plan in plans}, {(9, 'DP-2')})
        tracker.suppressed['0x4'] = 100
        tracker.observe([moved, first_new, second_new], MONITORS, now=8)
        self.assertNotIn('0x4', tracker.suppressed)

    def test_atomic_private_json_and_action_serialization(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'state/layout.json'
            memory.write_json(path, {'example': '中文'})
            self.assertEqual(memory.read_json(path, {}), {'example': '中文'})
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        record = memory.placement(window('0x1'), MONITORS)
        record['workspace'] = 4
        plan = memory.restore_plan(window('0x1'), record, MONITORS)
        with patch.object(memory, 'evaluate') as evaluate:
            memory.apply_plan(plan)
            self.assertIn('window="address:0x1"', evaluate.call_args.args[0])
            self.assertIn('workspace=4', evaluate.call_args.args[0])
        self.assertEqual(memory._lua('test";danger\n'), '"test\\";danger\\010"')

    def test_service_constructor_records_baseline_without_actions(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.object(memory, 'LAYOUT_FILE', Path(temporary) / 'layout.json'), \
                patch.object(memory, 'query', side_effect=[[window('0x1')], MONITORS]), \
                patch.object(memory, 'evaluate') as evaluate:
            service = memory.LayoutService()
            self.assertEqual(service.status()['tracked_windows'], 1)
            evaluate.assert_not_called()

    def test_new_login_preserves_saved_layout_but_same_session_restart_learns(self):
        old = memory.LayoutMemory()
        saved = window('0x1', title='project A', workspace=9, monitor=1)
        old.observe([saved], MONITORS, baseline=True, now=1)
        document = old.document()
        document['last_session'] = 'previous-login'
        current = window('0x2', title='project A')
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'layout.json'
            memory.write_json(path, document)
            with patch.object(memory, 'LAYOUT_FILE', path), \
                    patch.object(memory, 'query', side_effect=[[current], MONITORS]), \
                    patch.object(memory, 'evaluate') as evaluate:
                service = memory.LayoutService()
            evaluate.assert_not_called()
            self.assertEqual(service.memory.document()['windows'][0]['monitor'], 'DP-2')
            self.assertIn('0x2', service.memory.pending)
            document['last_session'] = memory.SESSION
            memory.write_json(path, document)
            with patch.object(memory, 'LAYOUT_FILE', path), \
                    patch.object(memory, 'query', side_effect=[[current], MONITORS]), \
                    patch.object(memory, 'evaluate') as evaluate:
                service = memory.LayoutService()
            evaluate.assert_not_called()
            self.assertEqual(service.memory.document()['windows'][0]['monitor'], 'DP-1')
            self.assertEqual(service.memory.pending, {})


if __name__ == '__main__':
    unittest.main()
