import numpy as np
import Xlib
import Xlib.display
import PIL.Image


class Window():
    def __init__(self, window, window_name, window_class):
        self.window = window
        self.window_name = window_name
        self.window_class = window_class

    def get_geometry(self):
        return self.window.get_geometry()

    def get_image(self, *args):
        return self.window.get_image(*args)


class Display():
    def __init__(self):
        self.disp, self.root = self.get_display_and_root()
        self.last_value = None
        self.NET_WM_NAME = self.disp.intern_atom('_NET_WM_NAME')
        self.NET_ACTIVE_WINDOW = self.disp.intern_atom('_NET_ACTIVE_WINDOW')
        self.NET_WM_CLASS = self.disp.intern_atom('_NET_WM_CLASS')
        # Listen for _NET_ACTIVE_WINDOW changes
        self.root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

    @staticmethod
    def get_display_and_root():
        disp = Xlib.display.Display()
        root = disp.screen().root
        return disp, root

    def get_window(self):
        try:
            window_id = self.root.get_full_property(
                self.NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
            active_window = self.disp.create_resource_object('window', window_id)
            window_class = " ".join(active_window.get_wm_class())
            window_name = active_window.get_full_property(self.NET_WM_NAME, 0).value
        except Xlib.error.XError:  # simplify dealing with BadWindow
            #self.disp, self.root = self.get_display_and_root()
            return None
        return Window(active_window, window_name, window_class)

    def get_window_info(self):
        active_window = self.get_window()

        if active_window is None:
            return self.last_value

        try:
            geo = active_window.get_geometry()
        except Xlib.error.XError:
            return self.last_value
        # verified okay
        # for gw in [0, 5, 10, 20, 30]:
        #     start_x = max(0, int(gw / 2) - 10)
        #     width = min(20, gw)
        #     print(gw, start_x, width)

        start_x = max(0, int(geo.width / 2) - 50)
        width = min(50, geo.width)

        start_y = max(0, int(geo.height / 2) - 50)
        height = min(50, geo.height)

        try:
            img = active_window.get_image(start_x, start_y, width,
                                          height, Xlib.X.ZPixmap, 0xffffffff)
        except Xlib.error.XError:
            return self.last_value

        img = PIL.Image.frombytes("RGB", (width, height), img.data, "raw", "BGRX")
        pixels = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)

        self.last_value = {
            "display_pixel_mean": pixels.mean(),
            "display_window_name": active_window.window_name.decode("utf8"),
            "display_window_class": active_window.window_class
        }
        # print(self.last_value)
        return self.last_value

    def main_thread_fn(self, adjust_brightness_fn):
        while True:
            event = self.disp.next_event()
            # Loop through, ignoring events until we're notified of focus/title change
            if event.type != Xlib.X.PropertyNotify:
                continue

            if event.atom in (self.NET_ACTIVE_WINDOW, self.NET_WM_NAME):
                self.get_window_info()
                adjust_brightness_fn()


if __name__ == "__main__":
    from threading import Thread
    d = Display()
    t = Thread(target=d.main_thread_fn, args=[print])
    t.start()
    while True:
        import time
        time.sleep(2)
        print(1)
    t.join()
    print(d.get_window_info())
