import os
import asyncio
import watchdog.observers
from watchdog.observers import Observer

from brightml.utils import get_brightml_path
from brightml.utils import ensure_path_exists
from brightml.utils import get_brightness_paths
from brightml.utils import ensure_latest_update_path

try:
    # ensure_future() has been introduced in Python 3.4.4
    from asyncio import ensure_future
except ImportError:
    from asyncio import async as ensure_future

watchdog.observers.inotify_buffer.InotifyBuffer.delay = 0

EVENT_TYPE_MOVED = 'moved'
EVENT_TYPE_DELETED = 'deleted'
EVENT_TYPE_CREATED = 'created'
EVENT_TYPE_MODIFIED = 'modified'


class AIOEventHandler(object):
    """An asyncio-compatible event handler."""

    def __init__(self, bml):
        self._loop = asyncio.get_event_loop()
        self.bml = bml
        self.task = None

    @asyncio.coroutine
    def on_modified(self, event):
        # if we wrote the update (meaning we triggered a brightness update)
        # then first wait
        if event.src_path.endswith("update"):
            yield from asyncio.sleep(0.2)
        # if there was an existing task, cancel it
        if self.task is not None:
            self.task.cancel()
        self.task = None
        # if the last event was a modified of one of the brightness files
        # then get features and retrain
        if not event.src_path.endswith("update"):
            self.task = ensure_future(self.bml.retrain())

    def dispatch(self, event):
        _method_map = {
            EVENT_TYPE_MODIFIED: self.on_modified,
        }
        handlers = [_method_map[event.event_type]]
        for handler in handlers:
            self._loop.call_soon_threadsafe(ensure_future, handler(event))


class AIOWatchdog(object):

    def __init__(self, paths, bml):
        self.observer = Observer()

        if not isinstance(paths, list):
            paths = [paths]

        evh = AIOEventHandler(bml)
        for path in paths:
            self.observer.schedule(evh, path, recursive=False)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


async def watch_fs(bml, brightml_path=None):
    if brightml_path is None:
        brightml_path = get_brightml_path()

    last_update_dir, _ = ensure_latest_update_path(brightml_path)

    monitored_paths = [last_update_dir] + get_brightness_paths()

    print(monitored_paths)
    watch = AIOWatchdog(monitored_paths, bml)
    watch.start()
    await asyncio.sleep(1000)
    watch.stop()
