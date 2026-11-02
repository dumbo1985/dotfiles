"""Shared, opt-in wttr.in weather for the bar and desktop panel."""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import re
import tempfile
import time
import urllib.parse
import urllib.request

CONFIG = Path(__file__).resolve().parent.parent
CITY_FILE = CONFIG / 'weather-city'
STATE = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'dotfiles-hyprland'
CACHE_FILE = STATE / 'weather-cache.json'
CACHE_SECONDS = 1800
RETRY_SECONDS = 300


def valid_city(value):
    value = str(value).strip()
    if not value or len(value) > 120 or re.search(r'[\x00-\x1f\x7f]', value):
        raise ValueError('请输入有效城市名称，不超过 120 个字符。')
    return value


def selected_city():
    value = os.environ.get('HYPR_WEATHER_CITY', '').strip()
    if not value:
        try:
            value = CITY_FILE.read_text().strip()
        except OSError:
            return ''
    try:
        return valid_city(value)
    except ValueError:
        return ''


def weather_url(city, data=False):
    path = urllib.parse.quote(valid_city(city), safe='')
    return 'https://wttr.in/' + path + ('?format=j1&lang=zh' if data else '?lang=zh')


def city_label(city):
    return '北京' if city.casefold() == 'beijing' else city


def condition_label(description):
    # wttr sometimes omits lang_zh even when requested; translate exact labels.
    labels = {'sunny': '晴', 'clear': '晴', 'partly cloudy': '局部多云', 'cloudy': '多云',
              'overcast': '阴', 'mist': '薄雾', 'fog': '雾', 'freezing fog': '冻雾',
              'light rain': '小雨', 'moderate rain': '中雨', 'heavy rain': '大雨',
              'light drizzle': '小毛毛雨', 'light snow': '小雪', 'moderate snow': '中雪',
              'heavy snow': '大雪', 'patchy rain nearby': '附近局部有雨',
              'patchy rain possible': '可能局部有雨', 'thundery outbreaks possible': '可能有雷暴'}
    return labels.get(description.strip().casefold(), description)


def read_cache(city):
    try:
        value = json.loads(CACHE_FILE.read_text())
        if value.get('city') == city:
            return value
    except (OSError, ValueError, AttributeError):
        pass
    return {'city': city, 'fetched_at': 0, 'attempted_at': 0}


def write_cache(value):
    STATE.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=STATE, prefix='weather-', delete=False) as file:
        temporary = Path(file.name)
        try:
            json.dump(value, file, ensure_ascii=False)
            file.flush()
            os.fsync(file.fileno())
            os.replace(temporary, CACHE_FILE)
        finally:
            temporary.unlink(missing_ok=True)


def number(value):
    value = str(value)
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', value):
        raise ValueError('Weather provider returned an invalid number')
    return value


def normalize(payload):
    current = payload['current_condition'][0]
    descriptions = current.get('lang_zh') or current.get('weatherDesc') or []
    description = str(descriptions[0]['value']).strip() if descriptions else ''
    if not description:
        raise ValueError('Weather provider returned no conditions')
    return {'temperature': number(current['temp_C']), 'feels_like': number(current['FeelsLikeC']),
            'humidity': number(current['humidity']), 'wind': number(current['windspeedKmph']),
            'description': description[:100], 'code': number(current['weatherCode'])}


def get_weather():
    city = selected_city()
    if not city:
        return {'city': '', 'state': 'unset', 'data': None, 'fetched_at': 0, 'stale': False}
    now = time.time()
    cached = read_cache(city)
    def result(value, state=None):
        age = now - value.get('fetched_at', 0)
        stale = bool(value.get('data')) and (age >= CACHE_SECONDS or value.get('failed', False))
        return {'city': city, 'state': state or ('ready' if value.get('data') else 'unavailable'),
                'data': value.get('data'), 'fetched_at': value.get('fetched_at', 0), 'stale': stale,
                'failed': value.get('failed', False)}
    if cached.get('data') and 0 <= now - cached.get('fetched_at', 0) < CACHE_SECONDS and not cached.get('failed'):
        return result(cached)
    if 0 <= now - cached.get('attempted_at', 0) < RETRY_SECONDS:
        return result(cached)
    STATE.mkdir(parents=True, exist_ok=True)
    with open(STATE / 'weather.lock', 'w') as lock:
        deadline = time.monotonic() + 5.2
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                # Both status bars start together. Wait for the shared request
                # rather than leave one screen displaying "loading" for 5 min.
                latest = read_cache(city)
                if latest.get('attempted_at', 0) != cached.get('attempted_at', 0):
                    return result(latest)
                if time.monotonic() >= deadline:
                    return result(latest, 'ready' if latest.get('data') else 'loading')
                time.sleep(.05)
        # The other screen may have refreshed between our first read and lock.
        cached = read_cache(city)
        if 0 <= now - cached.get('attempted_at', 0) < RETRY_SECONDS:
            return result(cached)
        cached['attempted_at'] = now
        try:
            request = urllib.request.Request(weather_url(city, data=True), headers={'User-Agent': 'HyprlandDesktopWeather/1.0'})
            with urllib.request.urlopen(request, timeout=5) as response:
                payload = json.loads(response.read(1024 * 1024))
            cached.update(data=normalize(payload), fetched_at=time.time(), failed=False)
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            cached['failed'] = True
        write_cache(cached)
        return result(cached)


def icon(code):
    code = int(float(code))
    if code == 113:
        return '󰖙'
    if code in (116, 119, 122):
        return '󰖐'
    if code in (143, 248, 260):
        return '󰖑'
    if code in (200, 386, 389, 392, 395):
        return '󰖓'
    if code in (179, 182, 185, 227, 230, 281, 284, 311, 314, 317, 320, 323, 326, 329, 332, 335, 338, 350, 362, 365, 368, 371, 374, 377):
        return '󰼶'
    return '󰖗'


def panel_summary(weather):
    if weather['state'] == 'unset':
        return '天气未设城市 · 点击顶栏天气设置'
    data = weather.get('data')
    if not data:
        return city_label(weather['city']) + (' · 天气读取中…' if weather['state'] == 'loading' else ' · 天气暂不可用')
    return f"{city_label(weather['city'])} · {data['temperature']}°C · {condition_label(data['description'])}" + (' · 缓存' if weather['stale'] else '')


def bar_status():
    weather = get_weather()
    instructions = '左键设置城市 · 右键查看当地天气'
    if weather['state'] == 'unset':
        return {'text': '󰖐 未设城市', 'tooltip': '天气尚未设置城市\n左键输入中文城市名或英文名称', 'class': 'unset'}
    data = weather.get('data')
    if not data:
        message = '读取中…' if weather['state'] == 'loading' else '天气不可用'
        return {'text': '󰖐 ' + message, 'tooltip': city_label(weather['city']) + '\n' + message + '\n' + instructions, 'class': weather['state']}
    stamp = time.strftime('%m-%d %H:%M', time.localtime(weather['fetched_at']))
    detail = [city_label(weather['city']) + ' · ' + condition_label(data['description']),
              f"气温 {data['temperature']}°C · 体感 {data['feels_like']}°C",
              f"湿度 {data['humidity']}% · 风速 {data['wind']} km/h", '更新于 ' + stamp]
    if weather['stale']:
        detail.append('网络更新失败，显示上次缓存' if weather.get('failed') else '正在刷新，显示上次缓存')
    detail.append(instructions)
    return {'text': f"{icon(data['code'])} {data['temperature']}°C" + (' 󰑐' if weather['stale'] else ''),
            'tooltip': '\n'.join(detail), 'class': 'stale' if weather['stale'] else 'ready'}
