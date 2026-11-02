"""Quick Look path handling, text bounds, PDF rendering and activation contract."""
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'config/lib'))
import file_preview as preview


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.storage = tempfile.TemporaryDirectory()
        self.root = Path(self.storage.name)

    def tearDown(self):
        self.storage.cleanup()

    def test_local_uri_spaces_and_remote_files(self):
        path = self.root / '中文 file.py'
        self.assertEqual(preview.local_path(path.as_uri()), path)
        self.assertEqual(preview.local_path('file://localhost' + str(path)), path)
        for value in ['https://example.com/file.pdf', 'smb://server/file', 'file://remote/path']:
            with self.assertRaises(ValueError):
                preview.local_path(value)

    def test_classification_does_not_execute_source_and_handles_binaries(self):
        source = self.root / 'run.py'
        source.write_text('raise RuntimeError("must never execute")\n')
        self.assertEqual(preview.inspect_file(source).kind, 'text')
        binary = self.root / 'binary'
        binary.write_bytes(b'\x7fELF\0\xff\x10')
        self.assertEqual(preview.inspect_file(binary).kind, 'metadata')
        self.assertEqual(preview.inspect_file(self.root).kind, 'directory')
        for name, kind in [('photo.png', 'image'), ('document.pdf', 'pdf'), ('movie.mp4', 'media')]:
            file = self.root / name
            file.touch()
            self.assertEqual(preview.inspect_file(file).kind, kind)

    def test_text_decoding_and_bounded_preview(self):
        path = self.root / 'text.txt'
        path.write_bytes('中文文本'.encode('utf-8'))
        self.assertEqual(preview.read_text(path), ('中文文本', False))
        path.write_bytes('中文'.encode('gb18030'))
        self.assertEqual(preview.read_text(path), ('中文', False))
        path.write_bytes(b'a' * 20)
        self.assertEqual(preview.read_text(path, 10), ('a' * 10, True))
        path.write_bytes(b'hello\0world')
        with self.assertRaises(ValueError):
            preview.read_text(path)
        path.write_bytes('中文'.encode('utf-16'))
        self.assertEqual(preview.read_text(path), ('中文', False))

    def test_directory_summary_hides_dotfiles_and_limits_rows(self):
        (self.root / '.hidden').touch()
        for index in range(25):
            (self.root / f'file-{index:02d}.txt').touch()
        summary = preview.directory_summary(self.root)
        self.assertNotIn('.hidden', summary)
        self.assertEqual(len(summary.splitlines()), 19)
        self.assertTrue(summary.endswith('…'))

    @unittest.skipUnless(Path('/usr/bin/pdftoppm').is_file(), 'system PDF renderer unavailable')
    def test_real_pdf_page_count_and_rasterization(self):
        try:
            import cairo
        except ImportError:
            self.skipTest('Cairo unavailable for PDF fixture')
        source = self.root / 'sample.pdf'
        surface = cairo.PDFSurface(str(source), 200, 200)
        context = cairo.Context(surface)
        for page in range(3):
            context.set_source_rgb(1, 1, 1)
            context.paint()
            context.set_source_rgb(0, 0, 0)
            context.move_to(10, 30)
            context.show_text(str(page + 1))
            context.show_page()
        surface.finish()
        self.assertEqual(preview.pdf_pages(source), 3)
        output = preview.render_pdf(source, 2, self.root / 'page2')
        self.assertTrue(output.read_bytes().startswith(b'\x89PNG\r\n'))

    def test_service_install_is_idempotent_and_uses_exact_nautilus_name(self):
        with patch.object(preview, 'DATA', self.root):
            service = preview.install_activation()
            content = service.read_text()
            timestamp = service.stat().st_mtime_ns
            self.assertEqual(preview.install_activation(), service)
            self.assertEqual(service.stat().st_mtime_ns, timestamp)
        self.assertIn('Name=org.gnome.NautilusPreviewer\n', content)
        self.assertIn('file-preview" --daemon', content)
        self.assertIn('org.gnome.NautilusPreviewer2', preview.INTROSPECTION)
        self.assertIn('name="Visible" type="b"', preview.INTROSPECTION)

    def test_existing_independent_preview_service_is_preserved(self):
        with patch.object(preview, 'DATA', self.root):
            path = self.root / 'dbus-1/services/org.gnome.NautilusPreviewer.service'
            path.parent.mkdir(parents=True)
            content = '[D-BUS Service]\nName=org.gnome.NautilusPreviewer\nExec=/usr/bin/sushi\n'
            path.write_text(content)
            self.assertEqual(preview.install_activation(), path)
            self.assertEqual(path.read_text(), content)

    def test_system_pdf_tool_ignores_temporary_path_override(self):
        if Path('/usr/bin/pdftoppm').is_file():
            with patch.dict(os.environ, {'PATH': '/tmp/codex-override'}):
                self.assertEqual(preview.system_program('pdftoppm'), '/usr/bin/pdftoppm')

    def test_pdf_renderer_cancels_and_reaps_process(self):
        cancel = threading.Event()
        cancel.set()
        with patch.object(preview, 'system_program', return_value='/bin/sleep'), \
                patch.object(preview.subprocess, 'Popen') as popen:
            process = popen.return_value
            process.poll.return_value = None
            with self.assertRaises(RuntimeError):
                preview.render_pdf(self.root / 'sample.pdf', 1, self.root / 'page', cancel)
            process.terminate.assert_called_once()
            process.wait.assert_called_once()


if __name__ == '__main__':
    unittest.main()
