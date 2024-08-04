from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from livewire.filesystem_sync import sync_zip
from livewire.filesystem_sync import Sync

from livewire import wait_forever, reloader, livewire_std_port
from livewire.httplib import HttpRoute, HttpResponse, HttpRequest
from livewire.webserver import Webserver


def start_hotreload_for(fs_root: Path, webserver_port: int = livewire_std_port):
    if not fs_root.exists():
        raise FileNotFoundError(f'path does not exist: {fs_root}')
    print(f'start_hotreload_for fs_root={fs_root}')

    if fs_root not in sys.path:
        sys.path.insert(0, str(fs_root))

    s = Webserver(webserver_port)

    def route(route_path):
        def wrapped(fn):
            def _safe_fn(req):
                try:
                    return fn(req)
                except Exception as e:
                    import traceback
                    msg = f'error in route {route_path}: {traceback.format_exc()}'
                    print(msg)
                    return HttpResponse.text_plain(msg, 500)

            s.set_http_route(HttpRoute(route_path, _safe_fn))
            return fn

        return wrapped

    root_state = _RootState(fs_root)

    @route('/')
    def index(req):
        return HttpResponse.text_plain(f'livewire.server up&running utcnow={datetime.utcnow()}')

    @route('/zip_init')
    def zip_target(req: HttpRequest):
        root_state.sync_init(sync_zip, req.body)
        return HttpResponse.text_plain(f'ok')

    @route('/zip_target')
    def zip_target(req: HttpRequest):
        root_state.sync_target(sync_zip, req.content)
        return HttpResponse.text_plain(f'ok')

    s.start_listen()
    wait_forever()


class _RootState:
    def __init__(self, fs_root: Path):
        self.fs_root = fs_root
        self.prev_finalize = None
        self.entrypoint_py = self.fs_root / 'entrypoint.py'

    def sync_init(self, sync: Sync, changes: bytes | str):
        self.sync_target(sync, changes)

    def sync_target(self, sync: Sync, changes_body: bytes | str):
        changes = json.loads(changes_body)
        if self.prev_finalize:
            print(f'running finalize of prev {self.entrypoint_py}')
            self.prev_finalize()
        else:
            print(f'no prev_finalize found in {self.entrypoint_py}')

        reloader.unload_path(str(self.fs_root))
        sync.sync_target(self.fs_root, changes)

        if self.entrypoint_py.exists():
            gl = dict()
            exec(self.entrypoint_py.read_text(), gl)
            self.prev_finalize = gl.get('finalize', None)


def main():
    fs_root = Path(sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='livewire-hotreload-'))
    start_hotreload_for(fs_root)


if __name__ == '__main__':
    main()
