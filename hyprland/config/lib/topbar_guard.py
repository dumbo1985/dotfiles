"""Restart only the top Waybar after crashes, within its Hyprland session."""
from __future__ import annotations

from collections import deque
import fcntl
import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time


MAX_RESTARTS = 5
RESTART_WINDOW = 60
RESTART_DELAY = 2


class TopbarGuard:
    def __init__(self, command, session_socket):
        self.command = command
        self.session_socket = Path(session_socket)
        self.stopped = threading.Event()
        self.child = None

    def stop(self, *_):
        self.stopped.set()
        if self.child is not None and self.child.poll() is None:
            try:
                self.child.terminate()
            except ProcessLookupError:
                pass

    def run(self):
        restarts = deque()
        while not self.stopped.is_set() and self.session_socket.exists():
            self.child = subprocess.Popen(self.command)
            if self.stopped.is_set():
                self.stop()
            status = self.child.wait()
            self.child = None
            # Theme reloads and explicit shutdowns use SIGTERM. Those should
            # leave the bar stopped until desktop-start launches it again.
            if self.stopped.is_set() or status in (0, -signal.SIGTERM, -signal.SIGINT,
                                                   128 + signal.SIGTERM, 128 + signal.SIGINT):
                return 0
            if not self.session_socket.exists():
                return 0
            now = time.monotonic()
            while restarts and now - restarts[0] >= RESTART_WINDOW:
                restarts.popleft()
            if len(restarts) >= MAX_RESTARTS:
                print('顶栏连续异常退出，已停止自动重试，请查看 waybar.log。', file=sys.stderr, flush=True)
                return 1
            restarts.append(now)
            print(f'顶栏异常退出（{status}），{RESTART_DELAY} 秒后重新启动。', file=sys.stderr, flush=True)
            if self.stopped.wait(RESTART_DELAY):
                return 0
        return 0


def main():
    signature = os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', '')
    if not signature:
        print('topbar-guard requires a Hyprland session', file=sys.stderr)
        return 1
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', f'/run/user/{os.getuid()}'))
    session_socket = runtime / 'hypr' / signature / '.socket.sock'
    config = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'hypr'
    state = runtime / 'hypr-theme'
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    session = hashlib.sha256(signature.encode()).hexdigest()[:12]
    with (state / f'topbar-{session}.lock').open('w') as lock:
        # Briefly allow the old guard to reap a terminated Waybar during a
        # theme restart, without accumulating indefinitely queued guards.
        deadline = time.monotonic() + 2
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    return 0
                time.sleep(.05)
        guard = TopbarGuard(['waybar', '--config', str(config / 'waybar.json'),
                            '--style', str(config / 'waybar.css')], session_socket)
        signal.signal(signal.SIGTERM, guard.stop)
        signal.signal(signal.SIGINT, guard.stop)
        return guard.run()


if __name__ == '__main__':
    raise SystemExit(main())
