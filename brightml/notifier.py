import os
import asyncio
import pyinotify

from brightml.brightness import BrightnessManager

from whereami.predict import Predicter

p = Predicter()

bm = BrightnessManager()

wm = pyinotify.WatchManager()  # Watch Manager
mask = pyinotify.ALL_EVENTS  # pyinotify.IN_MODIFY | pyinotify.IN_CLOSE_WRITE  # watched events

D = {}


async def whereami():
    D["whereami"] = p.predict()
    print(D["whereami"])
    await asyncio.sleep(30)
    asyncio.ensure_future(whereami())


async def train():
    await asyncio.sleep(1)
    print("training!")
    # print(D["whereami"])
    # asyncio.ensure_future(whereami())


class EventHandler(pyinotify.ProcessEvent):
    val = None

    def process_IN_CLOSE_WRITE(self, event):
        if self.val is not None:
            # prevent learning
            print("CANCEL")
            self.val.cancel()
        self.val = None
        print("Close write", event.pathname)

    def process_IN_MODIFY(self, event):
        # prevent doule tasks
        if self.val is not None:
            self.val.cancel()
        self.val = asyncio.ensure_future(train())
        print("Modify:", event.pathname)

    # def process_default(self, event):
    #    print(event)


handler = EventHandler()
loop = asyncio.get_event_loop()
loop.create_task(whereami())
notifier = pyinotify.AsyncioNotifier(wm, loop, default_proc_fun=handler)
# notifier = pyinotify.Notifier(wm, handler)

base_dir = "/sys/class/backlight/"
for path in os.listdir(base_dir):
    full_path = os.path.join(base_dir, path)
    print(full_path)
    wm.add_watch(full_path, mask)


async def fuck(x):
    asyncio.sleep(0)
    print("fuck", x)

if __name__ == '__main__':
    from threading import Thread
    from brightml.x11_active_window import main
    t = Thread(target=main, args=[lambda x: loop.create_task(fuck(x))])
    t.start()
    loop.run_forever()
    t.join()
