from PIL import Image
import pandas as pd
import numpy as np

data = pd.read_json("/home/pascal/.brightml/data.jsonl", lines=True)

# logic when to train model:
# after each update in brightness, but have an idle timer of 2 or 3 seconds

# logic at prediction:
# if ambient_light or active_window_class or active_window_name changes, then change brightness
final = data.groupby(["ambient_light", "active_window_class",
                      "datetime_date"]).last().reset_index()


images = [Image.open(x) for x in final["image_file_path"]]

images = np.array([np.array(x) for x in images])

images2 = [np.mean(i[:, 4:a]) for a, i in zip(final["active_window_width"], images)]

images2 = [np.mean(i[:, 4:a]) for a, i in zip(final["active_window_width"], images)]

# whereami does help
# pd.get_dummies(final["whereami"])
X = np.column_stack([final["ambient_light"], images2, final["datetime_hour"]])
y = np.clip(final["current_brightness"] + final["brightness_change"], 0, 1023)

from sklearn.ensemble import RandomForestRegressor

X = np.column_stack([final["ambient_light"], final["datetime_hour"], [np.mean(i[400:410, :][:, 1435:-1435]) for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images)], [np.mean(
    i[895:-895, :][:, 1435:-1435]) for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images)], pd.get_dummies(final["whereami"]), pd.get_dummies(final["active_window_class"])])
y = np.clip(final["current_brightness"] + final["brightness_change"], 0, 1023)
clf = RandomForestRegressor(1000)
clf.fit(X[::2], y[::2])
s = clf.score(X[1::2], y[1::2])
clf = RandomForestRegressor(100)
clf.fit(X[1::2], y[1::2])
s += clf.score(X[::2], y[::2])
print(s / 2)


from sklearn.metrics import mutual_info_score

X = np.column_stack([final["ambient_light"], images2, final["datetime_hour"]])
y = np.clip(final["current_brightness"] + final["brightness_change"], 0, 1023)


clf.fit(pd.get_dummies(final["whereami"]), y)

clf.score(pd.get_dummies(final["whereami"]), y)


np.corrcoef([np.mean(i[:, 4:a]) for a, i in zip(final["active_window_width"], images)], y)

for z in range(10, 100):
    print(z * 10)
    print(np.corrcoef([np.mean(i[z * 8:-z * 8, :][:, z * 12:-z * 12])
                       for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images)], y)[0][1])


for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images):
    print(xx, yy)

c_best = -1000
c_val = None
for j in range(1, 50):
    c = np.corrcoef([np.percentile(i[895:-895, :][:, 1435:-1435], 10)
                     for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images)], y)[0][1]
    c = np.abs(c)
    if c > c_best:
        print(c)
        c_val = j
        c_best = c


import PIL.Image

disp = Xlib.display.Display()
root = disp.screen().root

NET_WM_NAME = disp.intern_atom('_NET_WM_NAME')
NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')

while True:

    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        active_window = disp.create_resource_object('window', window_id)
        window_class = " ".join(active_window.get_wm_class())
        window_name = window.get_full_property(NET_WM_NAME, 0).value
    except Xlib.error.XError:  # simplify dealing with BadWindow
        window_name = None

    geo = active_window.get_geometry()

    # verified okay
    # for gw in [0, 5, 10, 20, 30]:
    #     start_x = max(0, int(gw / 2) - 10)
    #     width = min(20, gw)
    #     print(gw, start_x, width)

    start_x = max(0, int(geo.width / 2) - 200)
    width = min(200, geo.width)

    start_y = max(0, int(geo.height / 2) - 50)
    height = min(50, geo.height)

    img = active_window.get_image(start_x, start_y, width, height, Xlib.X.ZPixmap, 0xffffffff)

    img = PIL.Image.frombytes("RGB", (width, height), img.data, "raw", "BGRX")
    pixels = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)

    if window_class == "google-chrome Google-chrome":
        print(window_class, window_name)
        print(pixels.mean())
        print(sorted(pixels.ravel())[3750])
        img.show()
        input()
    time.sleep(0.3)


def bla():
    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        active_window = disp.create_resource_object('window', window_id)
        window_class = " ".join(active_window.get_wm_class())
        window_name = window.get_full_property(NET_WM_NAME, 0).value
    except Xlib.error.XError:  # simplify dealing with BadWindow
        window_name = None

    geo = active_window.get_geometry()

    # verified okay
    # for gw in [0, 5, 10, 20, 30]:
    #     start_x = max(0, int(gw / 2) - 10)
    #     width = min(20, gw)
    #     print(gw, start_x, width)

    start_x = max(0, int(geo.width / 2) - 50)
    width = min(50, geo.width)

    start_y = max(0, int(geo.height / 2) - 50)
    height = min(50, geo.height)

    img = active_window.get_image(start_x, start_y, width, height, Xlib.X.ZPixmap, 0xffffffff)

    img = PIL.Image.frombytes("RGB", (width, height), img.data, "raw", "BGRX")
    pixels = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
