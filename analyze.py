from PIL import Image
import pandas as pd
import numpy as np

data = pd.read_json("/home/pascal/.screensy/data.jsonl", lines=True)

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
X = np.column_stack([final["ambien>t_light"], images2, final["datetime_hour"]])
y = np.clip(final["current_brightness"] + final["brightness_change"], 0, 1023)

from sklearn.ensemble import RandomForestRegressor

clf = RandomForestRegressor(100)
clf.fit(X[::2], y[::2])
clf.score(X[1::2], y[1::2])


from sklearn.metrics import mutual_info_score

X = np.column_stack([final["ambient_light"], images2, final["datetime_hour"],
                     pd.get_dummies(final["whereami"])])
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


np.corrcoef([np.mean(i[895:-895, :][:, 1435:-1435])
             for xx, yy, i in zip(final["mouse_x"], final["mouse_y"], images)], y)


disp = Xlib.display.Display()
root = disp.screen().root

NET_WM_NAME = disp.intern_atom('_NET_WM_NAME')
NET_ACTIVE_WINDOW = disp.intern_atom('_NET_ACTIVE_WINDOW')

while True:

    try:
        window_id = root.get_full_property(NET_ACTIVE_WINDOW, Xlib.X.AnyPropertyType).value[0]
        window = disp.create_resource_object('window', window_id)
        window_class = " ".join(window.get_wm_class())
        window_name = window.get_full_property(NET_WM_NAME, 0).value
    except Xlib.error.XError:  # simplify dealing with BadWindow
        window_name = None
    print(window_class, window_name)

    time.sleep(0.3)
