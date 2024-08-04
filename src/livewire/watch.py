from __future__ import annotations

import json
import urllib.request
from datetime import timedelta
from pathlib import Path
from time import sleep
from typing import List, Any

from livewire.filesystem_sync import filesystemevents_print
from livewire.filesystem_sync import sync_zip
from livewire.filesystem_sync import Sync
from livewire.filesystem_sync.watchdog_debouncer import WatchdogDebouncer
from watchdog.events import FileSystemEvent

from livewire import livewire_std_port, wait_forever
from livewire.httplib import HttpResponse


def start_watch_for(watch_root: Path, host_port: str, debounce_millis=100):
    if not watch_root.exists():
        raise FileNotFoundError(f'path does not exist: {watch_root}')

    print(f'start_watch_for watch_root={watch_root}')
    url = f'http://{host_port}'
    print(f'pushing to {url}')

    sync: Sync = sync_zip
    init_pending = True

    def push_changes(changes: List) -> HttpResponse | None:
        nonlocal init_pending
        print(f'Pushing changes (length={len(changes)})')
        payload = json.dumps(changes)
        try:
            return _sync_fetch_response(f'{url}/zip_target', 'POST', payload)
        except Exception as ex:
            init_pending = True
            import traceback
            print(f'Push error: {ex} ({ex.__class__.__name__})')
            return None

    def callback(events: List[FileSystemEvent]):
        assert events
        filesystemevents_print(events)
        if init_pending:
            print('Init is pending. No sync will be sent for this batch.')
        changes = sync.sync_source(watch_root, events)
        push_changes(changes)

    debounced_watcher = WatchdogDebouncer(watch_root, timedelta(milliseconds=debounce_millis), callback)
    debounced_watcher.start()

    while True:
        while not init_pending:
            sleep(0.1)

        while init_pending:
            resp = push_changes(sync.sync_init(watch_root))
            if resp is not None and resp.code == 200:
                init_pending = False
                print('Init push sent.')
            else:
                sleep_secs = 5
                print(f'Failed to send initial push, retrying in {sleep_secs}...')
                sleep(sleep_secs)



def _sync_fetch_response(url: str, method: str = 'GET', data: str | bytes = '') -> HttpResponse:
    def make_response(r: Any) -> HttpResponse:
        return HttpResponse(200, r.read().decode("utf-8"), r.headers.get_content_type())

    if method != 'GET':
        if isinstance(data, str):
            data_bytes = bytes(data, 'utf8')
        else:
            data_bytes = data

        rq = urllib.request.Request(url, method=method, data=data_bytes)
        with urllib.request.urlopen(rq) as r:
            return make_response(r)
    else:
        with urllib.request.urlopen(url) as r:
            return make_response(r)


def main():
    # example: python -m livewire.watch push-to=10.2.2.14
    import argparse
    parser = argparse.ArgumentParser()
    # parser.add_argument('push_to', metavar='push-to', type=str,
    #                     help='Mandatory argument, define the ip address to push the changes to')
    parser.add_argument('--push-to', required=True, type=str, help='Target address to push to')
    parser.add_argument('port', action='store',
                        default=livewire_std_port, type=int,
                        nargs='?',
                        help=f'Specify alternate port [default: {livewire_std_port}]')

    args = parser.parse_args()
    host_port = f'{args.push_to}:{args.port}'

    watch_root = Path('.').absolute()
    start_watch_for(watch_root, host_port)
    wait_forever()


if __name__ == '__main__':
    main()
