"""Offline OCR cancellation, clipboard and whitespace behavior."""
from contextlib import contextmanager, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import screen_ocr as ocr


@contextmanager
def acquired():
    yield True


class OCRTests(unittest.TestCase):
    def test_selection_cancel_does_not_capture(self):
        cancelled = subprocess.CompletedProcess(['slurp'], 1, '', '')
        with patch.object(ocr.shutil, 'which', return_value='/bin/tool'), patch.object(ocr.subprocess, 'run', return_value=cancelled) as run:
            self.assertFalse(ocr.capture_region('/tmp/never-created.png'))
            self.assertEqual(run.call_count, 1)

    def test_empty_recognition_does_not_overwrite_clipboard(self):
        with patch.object(ocr, '_instance_lock', acquired), patch.object(ocr, 'dependencies', return_value={'available': True, 'wl-copy': '/bin/wl-copy'}), patch.object(ocr, 'process_file', return_value=''), patch.object(ocr, 'notify'), patch.object(ocr.subprocess, 'run') as run:
            self.assertEqual(ocr.main(['--file', '/tmp/input.png']), 0)
            run.assert_not_called()

    def test_cancelled_capture_does_not_recognize_or_copy(self):
        with patch.object(ocr, '_instance_lock', acquired), patch.object(ocr, 'dependencies', return_value={'available': True, 'wl-copy': '/bin/wl-copy'}), patch.object(ocr, 'capture_region', return_value=False), patch.object(ocr, 'process_file') as process, patch.object(ocr.subprocess, 'run') as run:
            self.assertEqual(ocr.main([]), 0)
            process.assert_not_called()
            run.assert_not_called()

    def test_code_mode_preserves_indentation_and_newlines(self):
        output = 'if (ready) {\n    return 42;\n}\n\x0c'
        result = subprocess.CompletedProcess(['tesseract'], 0, output, '')
        with patch.object(ocr, 'engine', return_value=('/bin/tesseract', {})), patch.object(ocr.subprocess, 'run', return_value=result) as run:
            self.assertEqual(ocr.recognize('/tmp/input.png', code=True), output.replace('\x0c', ''))
            command = run.call_args.args[0]
            self.assertIn('preserve_interword_spaces=1', command)
            self.assertIn('chi_sim+eng', command)

    def test_stdout_never_copies_or_notifies(self):
        output = io.StringIO()
        with patch.object(ocr, '_instance_lock', acquired), patch.object(ocr, 'dependencies', return_value={'available': True}), patch.object(ocr, 'process_file', return_value='Hello 世界\n'), patch.object(ocr, 'notify') as notify, patch.object(ocr.subprocess, 'run') as run, redirect_stdout(output):
            self.assertEqual(ocr.main(['--file', '/tmp/input.png', '--stdout']), 0)
            self.assertEqual(output.getvalue(), 'Hello 世界\n')
            run.assert_not_called()
            notify.assert_not_called()

    def test_normal_mode_joins_cjk_spacing_but_keeps_english_spaces(self):
        result = subprocess.CompletedProcess(['tesseract'], 0, '中 文 识别 ， 测 试 成 功 。\nHello world\n', '')
        with patch.object(ocr, 'engine', return_value=('/bin/tesseract', {})), patch.object(ocr.subprocess, 'run', return_value=result):
            self.assertEqual(ocr.recognize('/tmp/input.png'), '中文识别，测试成功。\nHello world\n')

    def test_code_line_boxes_restore_leading_indentation(self):
        text = 'if (ready) {\nreturn 42;\n}\n'
        tsv = 'level\tleft\twidth\n4\t43\t253\n4\t133\t202\n4\t44\t14\n'
        self.assertEqual(ocr._restore_indentation(text, tsv), 'if (ready) {\n    return 42;\n}\n')


if __name__ == '__main__':
    unittest.main()
