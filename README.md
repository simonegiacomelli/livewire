# livewire

A simple, fast, and lightweight live reload server for python modules.

## Server

The webserver is a simple python server that listens for two types of requests:
- sync_init, unload all modules, remove all the local filesystem and writes that files in the request payload, exec the entrypoint.py
- sync_target, unload all modules, update the deltas, exec the entrypoint.py

Example 
`python -m livewire.server`

Programmatically
```python
from livewire.server import start_hotreload_for
start_hotreload_for('/tmp/some-folder')
# the server is now running, you should block the main thread otherwise the process will exit
```

## Watch
The client watches the filesystem for changes and sends the requests to the server.

Example
`python -m livewire.watch --push-to=127.0.0.1`