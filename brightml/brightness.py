import time
import os

import numpy as np

from brightml.utils import get_brightml_path
from brightml.utils import ensure_latest_update_path


class BrightnessAdapter(object):
    def __init__(self, base_dir, name, brightml_path=None):
        path = base_dir + name + "/"
        self.name = name
        self.path = path
        _, self.update_path = ensure_latest_update_path(brightml_path)
        self.brightness_path = self.path + "brightness"
        self.max_brightness_path = self.path + "max_brightness"
        self.max_brightness = self._read_max_brightness()

    @property
    def brightness(self):
        return self._read_brightness()

    @brightness.setter
    def brightness(self, value):
        self._set_brightness(value)

    def _set_brightness(self, brightness):
        brightness = np.clip(int(brightness), 1, self.max_brightness)
        #print(self.name, self.brightness, brightness)
        with open(self.brightness_path, "w") as f:
            f.write(str(int(brightness)))
        with open(self.update_path, "w") as f:
            pass

    def _read_brightness(self):
        with open(self.brightness_path) as f:
            return int(f.read())

    def _read_max_brightness(self):
        with open(self.max_brightness_path) as f:
            return int(f.read())

    @property
    def is_valid(self):
        # if "intel" not in self.brightness_path:
        #     return False
        v = self.brightness
        self.brightness += 1
        v1 = self.brightness
        self.brightness -= 1
        v2 = self.brightness
        if v != v1 or v != v2:
            return True
        return False

    def __repr__(self):
        return "BrightnessAdapter(path='{}')".format(self.path)


class BrightnessManager(object):
    def __init__(self, base_dir="/sys/class/backlight/", validate=True):
        self.base_dir = base_dir
        self.adapters = [BrightnessAdapter(base_dir, x) for x in os.listdir(base_dir)]
        if validate:
            self.adapters = [x for x in self.adapters if x.is_valid]
        print(self.adapters)

    def get_percentage(self):
        m = 0
        n = 0
        for a in self.adapters:
            m += a.brightness / a.max_brightness
            n += 1
        return m / n

    def adapt(self, percentage_of_max=+5):
        for a in self.adapters:
            v = a.brightness
            m = a.max_brightness
            percentage_of_max = int(percentage_of_max)
            change_value = int(m * (abs(percentage_of_max) / 100))
            if percentage_of_max > 0 and v < m:
                a.brightness += change_value
            elif percentage_of_max < 0 and v > 1:
                a.brightness -= change_value

    def set_by_percentage(self, percentage):
        for a in self.adapters:
            a.brightness = a.max_brightness * (percentage / 100)

    def get_snapshot(self):
        return {x.name: x.brightness for x in self.adapters}

    def set_snapshot(self, snapshot):
        for s, a in zip(snapshot, self.adapters):
            a.brightness = s
