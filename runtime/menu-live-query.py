#!/usr/bin/python
"""Warm local currency/timezone data; never runs on a search keystroke."""
import fcntl
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

DIRECTORY = Path.home() / '.cache/omarchy'
CACHE = DIRECTORY / 'menu-fx.json'
ZONES = DIRECTORY / 'menu-zones.json'
SOURCE = 'https://www.cbr.ru/scripts/XML_daily.asp'
ZONE_NAMES = ('UTC', 'Europe/Moscow', 'Asia/Novosibirsk', 'Asia/Yekaterinburg',
              'Asia/Krasnoyarsk', 'Asia/Irkutsk', 'Asia/Vladivostok', 'Europe/London',
              'Europe/Paris', 'Europe/Berlin', 'Europe/Istanbul', 'Asia/Dubai',
              'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Seoul', 'Asia/Bangkok',
              'Asia/Almaty', 'Asia/Kolkata', 'America/New_York',
              'America/Los_Angeles', 'America/Chicago', 'Australia/Sydney')


def read_json(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def write_json(path, data):
    temporary = path.with_suffix(f'.{os.getpid()}.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False))
    temporary.replace(path)


def refresh():
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    with (DIRECTORY / 'menu-data.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        now = time.time()
        moment = datetime.now(timezone.utc)
        offsets = {name: int(moment.astimezone(ZoneInfo(name)).utcoffset().total_seconds() / 60)
                   for name in ZONE_NAMES}
        write_json(ZONES, {'offsets': offsets, 'updated_at': now})
        cached = read_json(CACHE)
        if cached.get('provider') == 'https://www.cbr.ru' and now - cached.get('fetched_at', 0) < 6 * 3600:
            return
        attempt_file = DIRECTORY / 'menu-fx-attempt.json'
        if now - read_json(attempt_file).get('attempt_at', 0) < 15 * 60:
            return
        write_json(attempt_file, {'attempt_at': now})
        try:
            request = urllib.request.Request(SOURCE, headers={'User-Agent': 'OmarchyMenu/2.0'})
            with urllib.request.urlopen(request, timeout=8) as response:
                xml = response.read(512 * 1024)
            root = ET.fromstring(xml)
            rates = {'RUB': 1.0}
            for item in root.findall('Valute'):
                code = item.findtext('CharCode', '')
                value = float(item.findtext('Value', '0').replace(',', '.'))
                nominal = float(item.findtext('Nominal', '1').replace(',', '.'))
                if len(code) == 3 and value > 0 and nominal > 0:
                    rates[code] = nominal / value
            if not all(code in rates for code in ('USD', 'EUR', 'CNY')):
                raise ValueError('Incomplete currency response')
            write_json(CACHE, {'base_code': 'RUB', 'rates': rates,
                              'provider': 'https://www.cbr.ru', 'date': root.attrib.get('Date', ''),
                              'fetched_at': now})
        except (OSError, ValueError, ET.ParseError):
            # Keep the last complete rates. The UI labels an old cache as such.
            return


if __name__ == '__main__':
    if '--refresh' in sys.argv:
        refresh()
