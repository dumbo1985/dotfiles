"""Unit conversions and opt-in dictionary lookups for desktop search."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import html
import json
import math
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

from launcher_search import Result


@dataclass(frozen=True)
class Unit:
    name: str
    dimension: str
    factor: float
    offset: float = 0


UNITS: dict[str, Unit] = {}


def _unit(name, dimension, factor, *aliases, offset=0):
    unit = Unit(name, dimension, factor, offset)
    for alias in (name, *aliases):
        UNITS[alias.casefold()] = unit


_unit('m', 'length', 1, 'meter', 'meters', 'metre', 'metres', '米')
_unit('km', 'length', 1000, 'kilometer', 'kilometers', 'kilometre', 'kilometres', '公里', '千米')
_unit('cm', 'length', .01, 'centimeter', 'centimeters', '厘米')
_unit('mm', 'length', .001, 'millimeter', 'millimeters', '毫米')
_unit('mile', 'length', 1609.344, 'mi', 'miles', '英里')
_unit('ft', 'length', .3048, 'foot', 'feet', '英尺')
_unit('in', 'length', .0254, 'inch', 'inches', '英寸')
_unit('yd', 'length', .9144, 'yard', 'yards', '码')
_unit('kg', 'mass', 1, 'kilogram', 'kilograms', '千克', '公斤')
_unit('g', 'mass', .001, 'gram', 'grams', '克')
_unit('mg', 'mass', .000001, 'milligram', 'milligrams', '毫克')
_unit('lb', 'mass', .45359237, 'lbs', 'pound', 'pounds', '磅')
_unit('oz', 'mass', .028349523125, 'ounce', 'ounces', '盎司')
_unit('s', 'time', 1, 'sec', 'second', 'seconds', '秒')
_unit('ms', 'time', .001, 'millisecond', 'milliseconds', '毫秒')
_unit('min', 'time', 60, 'minute', 'minutes', '分钟')
_unit('h', 'time', 3600, 'hr', 'hour', 'hours', '小时')
_unit('day', 'time', 86400, 'days', 'd', '天')
_unit('week', 'time', 604800, 'weeks', '周')
_unit('°C', 'temperature', 1, 'c', 'celsius', '摄氏度', offset=273.15)
_unit('°F', 'temperature', 5 / 9, 'f', 'fahrenheit', '华氏度', offset=273.15 - 32 * 5 / 9)
_unit('K', 'temperature', 1, 'kelvin', '开尔文')
_unit('m²', 'area', 1, 'm2', 'sqm', '平方米')
_unit('km²', 'area', 1000000, 'km2', '平方公里')
_unit('ft²', 'area', .09290304, 'ft2', 'sqft', '平方英尺')
_unit('ha', 'area', 10000, 'hectare', 'hectares', '公顷')
_unit('acre', 'area', 4046.8564224, 'acres', '英亩')
_unit('L', 'volume', 1, 'liter', 'liters', 'litre', 'litres', '升')
_unit('mL', 'volume', .001, 'milliliter', 'milliliters', '毫升')
_unit('m³', 'volume', 1000, 'm3', '立方米')
_unit('gal', 'volume', 3.785411784, 'gallon', 'gallons', 'usgal', '美制加仑')
_unit('m/s', 'speed', 1, 'mps', '米/秒')
_unit('km/h', 'speed', 1 / 3.6, 'kph', 'kmh', '公里/小时')
_unit('mph', 'speed', .44704, 'mile/h', 'miles/h', '英里/小时')
_unit('knot', 'speed', 1852 / 3600, 'knots', 'kt', '节')

DATA_UNITS: dict[str, Unit] = {}
for prefix, decimal, binary in (('', 1, 1), ('k', 1000, 1024), ('M', 1000**2, 1024**2),
                                ('G', 1000**3, 1024**3), ('T', 1000**4, 1024**4)):
    for suffix, bits in (('B', 8), ('b', 1)):
        name = prefix + suffix
        DATA_UNITS[name] = Unit(name, 'data', decimal * bits)
        if prefix:
            binary_name = prefix.upper() + 'i' + suffix
            DATA_UNITS[binary_name] = Unit(binary_name, 'data', binary * bits)
DATA_UNITS['KB'] = DATA_UNITS['kB']
DATA_UNITS['Kb'] = DATA_UNITS['kb']
for alias in ('byte', 'bytes', '字节'):
    DATA_UNITS[alias] = DATA_UNITS['B']
for alias in ('bit', 'bits', '比特'):
    DATA_UNITS[alias] = DATA_UNITS['b']

NUMBER = r'[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+)?'
CONVERSION = re.compile(r'^(' + NUMBER + r')\s*(.+?)\s*(?:\bto\b|\bin\b|->|→|转|换算成)\s*(.+?)\s*$', re.I)


def conversion(query: str) -> Result | None:
    text = query.strip()
    if text.casefold().startswith(('convert ', 'unit ')):
        text = text.split(None, 1)[1]
    match = CONVERSION.fullmatch(text)
    if not match:
        return None
    value, source_name, target_name = match.groups()
    source_name, target_name = source_name.strip(), target_name.strip()
    source = DATA_UNITS.get(source_name) or UNITS.get(source_name.casefold())
    target = DATA_UNITS.get(target_name) or UNITS.get(target_name.casefold())
    if not source or not target:
        return Result('无法换算', '未知单位；例如 10 km to mile、32 f to c、1 GB to MB', 'error', '', 'dialog-warning')
    if source.dimension != target.dimension:
        return Result('单位类型不匹配', f'{source_name} 和 {target_name} 不能互相换算', 'error', '', 'dialog-warning')
    try:
        number = float(value)
        base = number * source.factor + source.offset
        output = (base - target.offset) / target.factor
        if not math.isfinite(output) or abs(output) > 1e100:
            raise ValueError('数值超出范围')
        if source.dimension == 'temperature' and base < -1e-10:
            raise ValueError('温度不能低于绝对零度')
        if abs(output) < 1e-12:
            output = 0
        rendered = format(output, '.12g') + ' ' + target.name
        return Result(rendered, f'{value} {source.name} = {rendered}  ·  Enter 复制结果',
                      'conversion', rendered, 'accessories-calculator')
    except (OverflowError, ValueError) as error:
        return Result('无法换算', str(error), 'error', '', 'dialog-warning')


CACHE_AGE = 30 * 24 * 3600
MAX_RESPONSE = 1024 * 1024
WORD = re.compile(r"^[A-Za-z][A-Za-z '\-]{0,79}$")
OFFLINE = {
    'hypothetical': ('ˌhaɪpəˈθetɪkəl', 'adj. 假设的；假想的',
                     'Let us consider a hypothetical situation.', '让我们考虑一种假设的情景。'),
    'scenario': ('səˈnerioʊ', 'n. 情景；可能出现的局面',
                 'That is the worst-case scenario.', '那是最坏的情况。'),
    'exploitable': ('ɪkˈsplɔɪtəbəl', 'adj. 可被利用的；可被剥削的',
                    'This vulnerability is easily exploitable.', '这个漏洞很容易被利用。'),
    'reflexive': ('rɪˈfleksɪv', 'adj. 反身的；本能反应的',
                  'Myself is a reflexive pronoun.', 'myself 是一个反身代词。'),
    'reliable': ('rɪˈlaɪəbəl', 'adj. 可靠的；可信赖的',
                 'We need a reliable system.', '我们需要一个可靠的系统。'),
}


def _clean(value, limit=600):
    if not isinstance(value, str):
        return ''
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', '', value)).split())[:limit]


def _phonetic(value):
    value = _clean(value, 120).strip('/[] ')
    return '/' + value + '/' if value else ''


def _source(word, name='有道词典', url=None):
    url = url or 'https://dict.youdao.com/result?word=' + urllib.parse.quote(word) + '&lang=en'
    return Result('在词典中查看完整词条', name + ' · Enter 在浏览器打开', 'url', url, 'web-browser')


def _parse_youdao(data, word):
    if not isinstance(data, dict):
        return []
    entries = data.get('ec', {}).get('word', [])
    if not entries:
        return []
    entry = entries[0]
    returned = entry.get('return-phrase', {})
    if isinstance(returned, dict):
        returned = returned.get('l', {}).get('i', '')
    if returned and (not isinstance(returned, str) or returned.casefold() != word.casefold()):
        return []
    simple = data.get('simple', {}).get('word', [{}])[0]
    ipa = _phonetic(entry.get('usphone') or simple.get('usphone') or entry.get('ukphone'))
    pronunciation = '美式音标' if entry.get('usphone') or simple.get('usphone') else ('音标' if ipa else '该来源未提供音标')
    rows = [Result(word + ('  ' + ipa if ipa else ''),
                   pronunciation + ' · 有道词典 · Enter 复制',
                   'definition', word + (' ' + ipa if ipa else ''), 'accessories-dictionary')]
    meanings = []
    for group in entry.get('trs', []):
        for item in group.get('tr', []):
            values = item.get('l', {}).get('i', [])
            if isinstance(values, str):
                values = [values]
            for value in values:
                meaning = _clean(value)
                if meaning and meaning not in meanings:
                    meanings.append(meaning)
    if not meanings:
        return []
    rows.extend(Result(meaning, '释义 · Enter 复制', 'definition', meaning, 'accessories-dictionary')
                for meaning in meanings[:4])
    for example in data.get('blng_sents_part', {}).get('sentence-pair', [])[:2]:
        english = _clean(example.get('sentence') or example.get('sentence-eng'))
        chinese = _clean(example.get('sentence-translation'))
        if english:
            rows.append(Result(english, chinese or '例句 · Enter 复制', 'definition',
                               english + ('\n' + chinese if chinese else ''), 'text-x-generic'))
    rows.append(_source(word))
    return rows


def _parse_dictionaryapi(data, word):
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        return []
    entry = data[0]
    ipa = _phonetic(entry.get('phonetic') or next((item.get('text') for item in entry.get('phonetics', []) if item.get('text')), ''))
    rows = [Result(word + ('  ' + ipa if ipa else ''), 'DictionaryAPI · Enter 复制',
                   'definition', word + (' ' + ipa if ipa else ''), 'accessories-dictionary')]
    definitions, examples = [], []
    for meaning in entry.get('meanings', []):
        part = _clean(meaning.get('partOfSpeech'), 30)
        for definition in meaning.get('definitions', []):
            text = _clean(definition.get('definition'))
            if text:
                definitions.append(Result((part + '. ' if part else '') + text, '英文释义 · Enter 复制',
                                          'definition', text, 'accessories-dictionary'))
            example = _clean(definition.get('example'))
            if example and example not in examples:
                examples.append(example)
    if not definitions:
        return []
    rows.extend(definitions[:4])
    rows.extend(Result(example, '例句 · Enter 复制', 'definition', example, 'text-x-generic') for example in examples[:2])
    rows.append(_source(word, 'DictionaryAPI / Wiktionary',
                        'https://en.wiktionary.org/wiki/' + urllib.parse.quote(word)))
    return rows


def _cache_path(word):
    root = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home() / '.cache')))
    return root / 'dotfiles-hyprland/dictionary' / (word.replace(' ', '_') + '.json')


def _read_cache(word, fresh=True):
    try:
        path = _cache_path(word)
        if path.stat().st_size > 128 * 1024:
            return []
        data = json.loads(path.read_text())
        age = time.time() - data['timestamp']
        if data.get('version') != 1 or (fresh and (age < -86400 or age > CACHE_AGE)):
            return []
        rows = [Result(**item) for item in data['results'][:10]]
        valid = all(row.kind in ('definition', 'url')
                    and all(isinstance(value, str) for value in asdict(row).values())
                    and (row.kind != 'url' or row.target.startswith(('https://dict.youdao.com/', 'https://en.wiktionary.org/')))
                    for row in rows)
        return rows if valid else []
    except (OSError, TypeError, ValueError, KeyError):
        return []


def _write_cache(word, rows):
    path = _cache_path(word)
    temporary = None
    try:
        path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        handle, temporary = tempfile.mkstemp(prefix='.lookup-', dir=path.parent)
        with os.fdopen(handle, 'w') as stream:
            json.dump({'version': 1, 'timestamp': time.time(), 'results': [asdict(row) for row in rows]}, stream, ensure_ascii=False)
        os.replace(temporary, path)
    except OSError:
        pass
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)


def _fetch_json(url, deadline, cancel):
    remaining = deadline - time.monotonic()
    if remaining <= 0 or (cancel and cancel.is_set()):
        return None
    request = urllib.request.Request(url, headers={'User-Agent': 'dotfiles-desktop-dictionary/1.0', 'Accept': 'application/json'})
    with urllib.request.urlopen(request, timeout=min(1.4, remaining)) as response:
        raw = bytearray()
        while time.monotonic() < deadline and not (cancel and cancel.is_set()):
            chunk = response.read1(65536)
            if not chunk:
                return json.loads(raw)
            raw.extend(chunk)
            if len(raw) > MAX_RESPONSE:
                raise ValueError('Dictionary response exceeds limit')
    return None


def lookup_word(query: str, cancel=None) -> list[Result]:
    """Look up only an explicitly requested word; return cached results offline."""
    word = ' '.join(query.strip().casefold().split())
    if cancel and cancel.is_set():
        return []
    if not word:
        return [Result('输入要查询的英文单词', '例如 dict hypothetical · 显示音标、释义和例句', 'error', '', 'accessories-dictionary')]
    if not WORD.fullmatch(word):
        return [Result('请输入英文单词或短语', '例如 dict reliable', 'error', '', 'accessories-dictionary')]
    cached = _read_cache(word)
    if cached:
        return cached
    encoded = urllib.parse.quote(word)
    sources = [('https://dict.youdao.com/jsonapi?q=' + encoded + '&jsonversion=2', _parse_youdao),
               ('https://api.dictionaryapi.dev/api/v2/entries/en/' + encoded, _parse_dictionaryapi)]
    deadline = time.monotonic() + 3
    for url, parse in sources:
        if cancel and cancel.is_set():
            return []
        try:
            data = _fetch_json(url, deadline, cancel)
            if cancel and cancel.is_set():
                return []
            rows = parse(data, word)
            if rows:
                _write_cache(word, rows)
                return rows
        except (OSError, ValueError, TypeError, KeyError, IndexError, urllib.error.URLError):
            pass
    if cancel and cancel.is_set():
        return []
    cached = _read_cache(word, fresh=False)
    if cached:
        return cached
    if word in OFFLINE:
        ipa, meaning, english, chinese = OFFLINE[word]
        return [Result(word + '  /' + ipa + '/', '内置词条 · Enter 复制', 'definition', word + ' /' + ipa + '/', 'accessories-dictionary'),
                Result(meaning, '释义 · Enter 复制', 'definition', meaning, 'accessories-dictionary'),
                Result(english, chinese, 'definition', english + '\n' + chinese, 'text-x-generic'), _source(word)]
    return [Result('暂时未获取到词条', '可稍后重试，或选择下一项在网页词典中查询', 'error', '', 'dialog-information'), _source(word)]
