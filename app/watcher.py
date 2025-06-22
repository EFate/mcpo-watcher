import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

class ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, loop, callback_coro):
        self.loop = loop
        self.callback_coro = callback_coro

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and event.src_path.endswith("config.json"):
            print(f"Detected change in {event.src_path}. Triggering reload.")
            asyncio.run_coroutine_threadsafe(self.callback_coro(), self.loop)

def start_watching(path: str, loop, callback_coro):
    """启动文件监控。"""
    event_handler = ConfigChangeHandler(loop, callback_coro)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    print(f"Started watching for changes in directory: '{path}'")
    return observer