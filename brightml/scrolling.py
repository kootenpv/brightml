import time
from pynput.mouse import Listener
from cachetools import TTLCache
from brightml.features import d

ttl = TTLCache(20, 0.2)

# TODO
# what needs to be fixed is actually that it also affects the capturing the pixel


def adjust(adjust_brightness_fn):
    def on_scroll(x, y, dx, dy):
        print('Scrolled {0}'.format((x, y)))
        ttl[time.time()] = 1
        if len(ttl) == 19:
            print("scrolled seriously")
            d.get_window_info()
            adjust_brightness_fn(True)

    return on_scroll


def scroll_listen(adjust_brightness_fn):
    while True:
        print("OK")
        with Listener(on_scroll=adjust(adjust_brightness_fn)) as listener:
            listener.join()
