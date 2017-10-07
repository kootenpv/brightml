import os
import sys
import json
import time
from datetime import datetime
from Xlib import display
import Xlib
import numpy as np

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

# data = sorted(just.iread("/home/pascal/.screensy/data.jsonl"), key=lambda x: x["datetime_full"])


def change_brightness():
    if len(sys.argv) > 1:
        change = sys.argv[1]
        os.system("gmux_backlight " + change)
        return int(change)
    return None


def get_image_file_path(image_path, datetime_full):
    image_file_path = datetime_full
    for x in ":+ ":
        image_file_path = image_file_path.replace(x, "_")
    return os.path.join(image_path, image_file_path) + ".png"


def get_image(root, geo):
    return root.get_image(0, 0, geo.width, geo.height, Xlib.X.ZPixmap, 0xffffffff)


def save_image(root, geo, image_file_path):
    import PIL.Image
    ximage = get_image(root, geo)
    img = PIL.Image.frombytes("RGB", (geo.width, geo.height), ximage.data, "raw", "BGRX")
    img.save(image_file_path)


def get_ambient_light():
    with open("/sys/devices/platform/applesmc.768/light") as f:
        return int(f.read()[1:-1].split(",")[0])


def get_current_brightness():
    with open("/sys/class/backlight/gmux_backlight/brightness") as f:
        return int(f.read())


def get_max_brightness():
    with open("/sys/class/backlight/gmux_backlight/max_brightness") as f:
        return int(f.read())


def get_whereami():
    try:
        from whereami import predict
        return predict()
    except:
        return "None"


def get_features(data_path):
    current_brightness = get_current_brightness()
    brightess_change = change_brightness()

    # local time (does not have microsecond)
    now = datetime.strptime(time.strftime(DATE_FORMAT, time.localtime()), DATE_FORMAT)
    microsecond = datetime.now().microsecond
    # add microsecond for uniqueness
    now = now.replace(microsecond=microsecond)
    datetime_full = str(now)

    # paths
    data_path = os.path.expanduser(data_path)

    image_path = os.path.join(data_path, "images")

    disp = display.Display()
    root = disp.screen().root

    geo = root.get_geometry()

    # active window
    active_window = disp.get_input_focus().focus
    active_window_geo = active_window.get_geometry()

    # image file path
    image_file_path = get_image_file_path(image_path, datetime_full)
    save_image(root, geo, image_file_path)

    # mouse
    mouse_data = root.query_pointer()

    all_data = {
        "ambient_light": get_ambient_light(),
        "current_brightness": current_brightness,
        "brightness_change": brightess_change,
        "max_brightness": get_max_brightness(),
        "mouse_x": mouse_data.root_x,
        "mouse_y": mouse_data.root_y,
        "active_window_name": active_window.get_wm_name(),  # Out[60]: '*IPython3*'
        "active_window_class": " ".join(active_window.get_wm_class()),  # Out: ('emacs', 'Emacs'),
        "image_file_path": image_file_path,

        # just because we can
        "whereami": get_whereami(),

        # seems wrong
        "active_window_x": active_window_geo.x,
        "active_window_y": active_window_geo.y,
        "active_window_width": active_window_geo.width,
        "active_window_height": active_window_geo.height,
        "root_width": geo.width,
        "root_height": geo.height,
        "datetime_full": datetime_full,

        # TODO: do something with hour + timezone w.r.t. sunrize / sunset
        "datetime_hour": now.hour,
        "datetime_timezone": str(now.tzinfo),
        "datetime_time": str(now.time()),
        "datetime_date": str(now.date()),
    }
    with open(data_path + "/data.jsonl", "a") as f:
        f.write(json.dumps(all_data) + "\n")
    print(json.dumps(all_data, indent=4))


if __name__ == "__main__":
    get_features("~/.screensy")


def bla():
    disp = display.Display()
    root = disp.screen().root

    geo = root.get_geometry()

    # active window
    active_window = disp.get_input_focus().focus
    geo = active_window.get_geometry()

    # verified okay
    # for gw in [0, 5, 10, 20, 30]:
    #     start_x = max(0, int(gw / 2) - 10)
    #     width = min(20, gw)
    #     print(gw, start_x, width)

    start_x = max(0, int(geo.width / 2) - 10)
    width = min(20, geo.width)

    start_y = max(0, int(geo.height / 2) - 10)
    height = min(20, geo.height)

    img = active_window.get_image(start_x, start_y, width, height, Xlib.X.ZPixmap, 0xffffffff)

    img = PIL.Image.frombytes("RGB", (width, height), img.data, "raw", "BGRX")
    pixels = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)

    return pixels.mean()
