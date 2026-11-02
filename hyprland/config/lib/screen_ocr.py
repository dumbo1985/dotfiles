"""Recognize a selected screen region locally, then copy its text."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import csv
import fcntl
import io
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

DATA = Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))
LOCAL = DATA / 'hypr-ocr'
MAX_PIXELS = 32000000


class OCRError(RuntimeError):
    pass


def _environment():
    environment = os.environ.copy()
    tools = DATA / 'hypr-theme/bin'
    environment['PATH'] = str(Path.home() / '.local/bin') + ':' + str(tools) + ':' + environment.get('PATH', '/usr/bin:/bin')
    # Apply private libraries only to OCR children, never the desktop session.
    environment['OMP_THREAD_LIMIT'] = '2'
    return environment


def engine():
    environment = _environment()
    local = LOCAL / 'usr/bin/tesseract'
    if local.is_file():
        environment['LD_LIBRARY_PATH'] = str(LOCAL / 'usr/lib/x86_64-linux-gnu')
        environment['TESSDATA_PREFIX'] = str(LOCAL / 'usr/share/tesseract-ocr/5/tessdata')
        return str(local), environment
    return shutil.which('tesseract', path=environment['PATH']), environment


def dependencies():
    executable, environment = engine()
    languages, error = [], ''
    if executable:
        try:
            result = subprocess.run([executable, '--list-langs'], env=environment,
                                    capture_output=True, text=True, timeout=5)
            if result.returncode:
                error = result.stderr.strip()[:300] or 'Tesseract 无法运行'
            else:
                languages = [line.strip() for line in result.stdout.splitlines() if re.fullmatch(r'[a-z_]+', line.strip())]
        except (OSError, subprocess.SubprocessError) as failure:
            error = str(failure)
    else:
        error = '未找到 Tesseract；请部署本地 OCR 引擎及 eng、chi_sim 语言数据'
    return {'available': bool(executable and not error and {'eng', 'chi_sim'} <= set(languages)),
            'engine': executable, 'languages': languages, 'local_directory': str(LOCAL),
            'slurp': shutil.which('slurp', path=environment['PATH']),
            'grim': shutil.which('grim', path=environment['PATH']),
            'wl-copy': shutil.which('wl-copy', path=environment['PATH']), 'error': error}


def notify(title, message=''):
    try:
        subprocess.run(['notify-send', '-a', '屏幕文字识别', '-t', '3500', title, message],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    except (OSError, subprocess.SubprocessError):
        pass


def _runtime():
    runtime = Path(os.environ.get('XDG_RUNTIME_DIR', '/run/user/' + str(os.getuid())))
    if runtime.is_dir():
        return runtime
    cache = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))) / 'dotfiles-hyprland/ocr-runtime'
    cache.mkdir(parents=True, mode=0o700, exist_ok=True)
    return cache


@contextmanager
def _instance_lock():
    path = _runtime() / 'hypr-screen-ocr.lock'
    with path.open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            yield False
            return
        yield True


def capture_region(destination):
    environment = _environment()
    slurp = shutil.which('slurp', path=environment['PATH'])
    grim = shutil.which('grim', path=environment['PATH'])
    if not slurp or not grim:
        raise OCRError('缺少 slurp 或 grim，无法框选屏幕')
    try:
        selection = subprocess.run([slurp, '-d', '-b', '#0d0f19aa', '-c', '#7aa2f7ff', '-w', '2'],
                                   env=environment, capture_output=True, text=True, timeout=180)
        # Escape/right click deliberately cancels; do not modify the clipboard.
        if selection.returncode or not selection.stdout.strip():
            return False
        geometry = selection.stdout.strip()
        region = re.fullmatch(r'-?\d+,-?\d+ ([1-9]\d*)x([1-9]\d*)', geometry)
        if not region:
            raise OCRError('框选区域格式不正确')
        if int(region[1]) * int(region[2]) > MAX_PIXELS:
            raise OCRError('框选区域过大，请缩小到需要识别的文字')
        time.sleep(.12)
        result = subprocess.run([grim, '-g', geometry, str(destination)], env=environment,
                                capture_output=True, text=True, timeout=10)
        if result.returncode or not Path(destination).is_file():
            raise OCRError('无法读取屏幕画面：' + result.stderr.strip()[:250])
        return True
    except subprocess.TimeoutExpired as failure:
        raise OCRError('框选或截图超时，请重新操作') from failure


def _prepare_image(source, destination):
    try:
        from PIL import Image, ImageOps
        with Image.open(source) as image:
            width, height = image.size
            if width * height > MAX_PIXELS or width <= 0 or height <= 0:
                raise OCRError('图片过大，请缩小到需要识别的文字区域')
            image = ImageOps.exif_transpose(image).convert('RGB')
            # Enlarging small glyphs helps screenshot text. Enlarging already
            # large glyphs can make Chinese recognition worse, so measure the
            # foreground row bands instead of guessing from crop dimensions.
            bands = []
            gray = image.convert('L')
            if gray.getextrema()[1] - gray.getextrema()[0] >= 40:
                threshold = gray.point(lambda pixel: 255 if pixel < 150 else 0)
                active = []
                for row in range(height):
                    count = threshold.crop((0, row, width, row + 1)).histogram()[255]
                    active.append(min(count, width - count) >= max(2, width * .002))
                start = None
                for row, ink in enumerate(active + [False]):
                    if ink and start is None:
                        start = row
                    elif not ink and start is not None:
                        if row - start >= 6:
                            bands.append(row - start)
                        start = None
            median = sorted(bands)[len(bands) // 2] if bands else 30
            if median < 26 and width * height * 4 <= MAX_PIXELS:
                image = image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
            image.save(destination, format='PNG', dpi=(300, 300))
    except OCRError:
        raise
    except (OSError, ValueError) as failure:
        raise OCRError('无法读取图片：' + str(failure)) from failure
    except ImportError as failure:
        raise OCRError('缺少 Python Pillow，无法预处理图片') from failure


def recognize(image, code=False):
    executable, environment = engine()
    if not executable:
        raise OCRError('尚未部署 Tesseract OCR 引擎')
    command = [executable, str(Path(image).absolute()), 'stdout', '-l', 'chi_sim+eng', '--psm', '6',
               '-c', 'preserve_interword_spaces=' + ('1' if code else '0')]
    try:
        result = subprocess.run(command, env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding='utf-8', errors='replace', timeout=30)
    except subprocess.TimeoutExpired as failure:
        raise OCRError('文字识别超时，请缩小框选区域后重试') from failure
    except OSError as failure:
        raise OCRError('无法启动 OCR 引擎：' + str(failure)) from failure
    if result.returncode:
        raise OCRError('文字识别失败：' + result.stderr.strip()[:350])
    text = result.stdout.replace('\r\n', '\n').replace('\x0c', '')
    if not text.strip():
        return ''
    if code:
        # Plain Tesseract text preserves internal gaps but drops leading
        # indentation. Its line boxes let us restore approximate code columns.
        try:
            geometry = subprocess.run(command + ['tsv'], env=environment, capture_output=True,
                                      text=True, encoding='utf-8', errors='replace', timeout=10)
            if geometry.returncode == 0:
                text = _restore_indentation(text, geometry.stdout)
        except (OSError, subprocess.SubprocessError, ValueError, KeyError):
            pass
    if not code:
        # Tesseract often inserts spaces between individual CJK characters.
        text = re.sub(r'(?<=[\u3400-\u9fff])[ \t]+(?=[\u3400-\u9fff\u3000-\u303f\uff00-\uffef])', '', text)
        text = re.sub(r'(?<=[\u3000-\u303f\uff00-\uffef])[ \t]+(?=[\u3400-\u9fff])', '', text)
    return text.rstrip('\n') + '\n' if code else text.strip() + '\n'


def _restore_indentation(text, tsv):
    boxes = [row for row in csv.DictReader(io.StringIO(tsv), delimiter='\t') if row.get('level') == '4']
    lines = text.splitlines()
    nonempty = [line for line in lines if line.strip()]
    if not boxes or len(boxes) != len(nonempty):
        return text
    widths = [int(box['width']) / max(1, len(line.strip()) - .35)
              for box, line in zip(boxes, nonempty) if len(line.strip()) >= 4]
    if not widths:
        return text
    pitch = statistics.median(widths)
    if pitch < 2:
        return text
    origin = min(int(box['left']) for box in boxes)
    restored, index = [], 0
    for line in lines:
        if not line.strip():
            restored.append(line)
            continue
        column = max(0, min(160, round((int(boxes[index]['left']) - origin) / pitch)))
        existing = len(line) - len(line.lstrip(' '))
        restored.append(' ' * max(column, existing) + line.lstrip(' '))
        index += 1
    return '\n'.join(restored) + ('\n' if text.endswith('\n') else '')


def process_file(path, code=False):
    image = Path(path).expanduser().absolute()
    if not image.is_file():
        raise OCRError('找不到图片：' + str(image))
    if image.stat().st_size > 64 * 1024 * 1024:
        raise OCRError('图片文件超过 64 MB，请先裁剪')
    with tempfile.TemporaryDirectory(prefix='hypr-ocr-image-', dir=_runtime()) as temporary:
        prepared = Path(temporary) / 'prepared.png'
        _prepare_image(image, prepared)
        return recognize(prepared, code)


def main(argv=None):
    parser = argparse.ArgumentParser(description='框选屏幕，离线识别中英文并复制到剪贴板。Esc 取消。')
    parser.add_argument('--code', action='store_true', help='保留代码换行与词间空格')
    parser.add_argument('--file', metavar='PATH', help='识别已有图片，不进行框选')
    parser.add_argument('--stdout', action='store_true', help='只输出文字，不复制、不显示通知')
    parser.add_argument('--check', action='store_true', help='以 JSON 输出依赖状态')
    args = parser.parse_args(argv)
    if args.check:
        status = dependencies()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        return 0 if status['available'] else 1
    os.umask(0o077)
    try:
        with _instance_lock() as acquired:
            if not acquired:
                if not args.stdout:
                    notify('文字识别正在进行', '请先完成或取消当前框选')
                return 0
            status = dependencies()
            if not status['available']:
                raise OCRError(status['error'] or '缺少 eng 或 chi_sim 语言数据')
            if args.file:
                if not args.stdout:
                    notify('正在识别图片文字…', '在本机处理，中英文均可')
                text = process_file(args.file, args.code)
            else:
                with tempfile.TemporaryDirectory(prefix='hypr-ocr-capture-', dir=_runtime()) as temporary:
                    image = Path(temporary) / 'capture.png'
                    if not capture_region(image):
                        return 0
                    if not args.stdout:
                        notify('正在识别屏幕文字…', '在本机处理，中英文均可')
                    text = process_file(image, args.code)
            if not text:
                if not args.stdout:
                    notify('没有识别到文字', '剪贴板内容保持不变；可尝试框选更清晰的区域')
                return 0
            if args.stdout:
                sys.stdout.write(text)
            else:
                if not status['wl-copy']:
                    raise OCRError('缺少 wl-copy，无法复制识别结果')
                subprocess.run([status['wl-copy']], input=text.encode('utf-8'), check=True, timeout=3,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                notify('识别结果已复制', f'{len(text.strip())} 个字符' + (' · 保留代码换行与空格' if args.code else ''))
            return 0
    except (OCRError, OSError, subprocess.SubprocessError) as failure:
        message = str(failure)
        print(message, file=sys.stderr)
        if not args.stdout:
            notify('文字识别未完成', message[:300])
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
