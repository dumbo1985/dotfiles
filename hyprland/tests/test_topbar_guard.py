"""Top-bar recovery lifecycle without launching or signalling desktop processes."""
from contextlib import redirect_stderr
import io
from pathlib import Path
import signal
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import topbar_guard as topbar


class TopbarGuardTests(unittest.TestCase):
    def guard(self):
        guard = topbar.TopbarGuard(['waybar', '--config', '/test/waybar.json'], '/test/session.sock')
        guard.session_socket = Mock()
        guard.session_socket.exists.return_value = True
        guard.stopped = Mock()
        guard.stopped.is_set.return_value = False
        guard.stopped.wait.return_value = False
        return guard

    def test_clean_and_deliberate_signal_exits_do_not_restart(self):
        for status in (0, -signal.SIGTERM, -signal.SIGINT,
                       128 + signal.SIGTERM, 128 + signal.SIGINT):
            with self.subTest(status=status):
                guard = self.guard()
                process = Mock()
                process.wait.return_value = status
                with patch.object(topbar.subprocess, 'Popen', return_value=process) as launch:
                    self.assertEqual(guard.run(), 0)
                launch.assert_called_once_with(guard.command)
                guard.stopped.wait.assert_not_called()

    def test_crash_restarts_after_delay_and_reaps_each_child(self):
        guard = self.guard()
        crashed, restarted = Mock(), Mock()
        crashed.wait.return_value = -signal.SIGSEGV
        restarted.wait.return_value = 0
        with patch.object(topbar.subprocess, 'Popen', side_effect=[crashed, restarted]) as launch, \
                redirect_stderr(io.StringIO()):
            self.assertEqual(guard.run(), 0)
        self.assertEqual(launch.call_count, 2)
        guard.stopped.wait.assert_called_once_with(topbar.RESTART_DELAY)
        crashed.wait.assert_called_once()
        restarted.wait.assert_called_once()
        self.assertIsNone(guard.child)

    def test_session_ending_after_crash_stops_recovery(self):
        guard = self.guard()
        guard.session_socket.exists.side_effect = [True, False]
        process = Mock()
        process.wait.return_value = -signal.SIGSEGV
        with patch.object(topbar.subprocess, 'Popen', return_value=process) as launch:
            self.assertEqual(guard.run(), 0)
        launch.assert_called_once()
        guard.stopped.wait.assert_not_called()

    def test_shutdown_during_delay_does_not_spawn_another_child(self):
        guard = self.guard()
        guard.stopped.wait.return_value = True
        process = Mock()
        process.wait.return_value = 1
        with patch.object(topbar.subprocess, 'Popen', return_value=process) as launch, \
                redirect_stderr(io.StringIO()):
            self.assertEqual(guard.run(), 0)
        launch.assert_called_once()

    def test_repeated_crashes_hit_restart_limit(self):
        guard = self.guard()
        process = Mock()
        process.wait.return_value = -signal.SIGSEGV
        with patch.object(topbar.subprocess, 'Popen', return_value=process) as launch, \
                patch.object(topbar.time, 'monotonic', return_value=10), \
                redirect_stderr(io.StringIO()):
            self.assertEqual(guard.run(), 1)
        self.assertEqual(launch.call_count, topbar.MAX_RESTARTS + 1)
        self.assertEqual(guard.stopped.wait.call_count, topbar.MAX_RESTARTS)

    def test_old_crashes_expire_from_restart_budget(self):
        guard = self.guard()
        processes = [Mock() for _ in range(topbar.MAX_RESTARTS + 3)]
        for process in processes[:-1]:
            process.wait.return_value = 1
        processes[-1].wait.return_value = 0
        times = [index * topbar.RESTART_WINDOW for index in range(len(processes))]
        with patch.object(topbar.subprocess, 'Popen', side_effect=processes) as launch, \
                patch.object(topbar.time, 'monotonic', side_effect=times), \
                redirect_stderr(io.StringIO()):
            self.assertEqual(guard.run(), 0)
        self.assertEqual(launch.call_count, len(processes))

    def test_guard_shutdown_terminates_only_its_own_live_child(self):
        guard = self.guard()
        process = Mock()
        process.poll.return_value = None
        guard.child = process
        guard.stop()
        guard.stopped.set.assert_called_once()
        process.terminate.assert_called_once()

    def test_disappearing_child_during_shutdown_is_harmless(self):
        guard = self.guard()
        process = Mock()
        process.poll.return_value = None
        process.terminate.side_effect = ProcessLookupError
        guard.child = process
        guard.stop()
        guard.stopped.set.assert_called_once()


if __name__ == '__main__':
    unittest.main()
