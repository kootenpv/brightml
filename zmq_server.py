import os
import time
import zmq
from zmq_timer import ZmqTimer, ZmqTimerManager

from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor

from whereami.predict import Predicter
from display import Display

from sklearn.preprocessing import OneHotEncoder

p = Predicter("/home/pascal/.whereami/")
d = Display()

main_clf = None
old_value = None

le = {}
ohe = OneHotEncoder(handle_unknown="ignore")

# todo: chargedness of battery

train_samples = [('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79),
                 ('bed', 0, 'pascal@archbook:~/egoroot/screensy', 'urxvt URxvt', 0.0, 0, 1078),
                 ('bed', 0, 'OSError: [Errno 22] Invalid argument - Google Search - Google Chrome',
                  'google-chrome Google-chrome', 255.0, 0, 79)]


with open("/sys/class/backlight/gmux_backlight/max_brightness") as f:
    MAX_BRIGHTNESS = int(f.read())


def get_current_brightness():
    with open("/sys/class/backlight/gmux_backlight/brightness") as f:
        return int(f.read())


def write_brightness(brightness):
    brightness = int(brightness)
    with open("/sys/class/backlight/gmux_backlight/brightness", "w") as f:
        f.write(str(brightness))


def get_ambient_light():
    with open("/sys/devices/platform/applesmc.768/light") as f:
        return int(f.read()[1:-1].split(",")[0])


def labelize(x):
    if x not in le:
        le[x] = len(le)
    return le[x]


def adjust_brightness():
    global last_train_sample
    global old_value
    if last_train_sample is None and main_clf is not None:
        ambient = get_ambient_light()
        window_name, window_class, pixel_mean = d.last_value
        # comparison for checking if should update
        new_value = (p.predicted_value, ambient, window_name, window_class)
        if old_value != new_value:
            X = (new_value + (pixel_mean, datetime.now().hour))
            print("NEW STATE", X)
            X = [[labelize(y) if isinstance(y, str) else y for y in X]]
            X = ohe.transform(X)
            if main_clf:
                try:
                    pred = main_clf.predict(X)[0]
                    print("NEW BRIGHTNESS", pred)
                    write_brightness(np.clip(pred, 1, MAX_BRIGHTNESS))
                except ValueError as e:
                    print(e)
                    return
            else:
                print("PREDICTING!")
            old_value = new_value


last_add_train = time.time()
last_train_sample = None


def add_train(bright_change):
    global last_add_train
    global last_train_sample

    os.system("gmux_backlight " + bright_change)
    last_add_train = time.time()

    ambient = get_ambient_light()
    window_name, window_class, pixel_mean = d.last_value
    # comparison for checking if should update
    last_train_sample = (p.predicted_value, ambient, window_name, window_class,
                         pixel_mean, datetime.now().hour, get_current_brightness() + int(bright_change))

    print("RECEIVED added training", last_train_sample)
    print("OK", bright_change)


def retrain():
    global last_train_sample
    global last_add_train
    global main_clf
    if last_train_sample is not None:
        t1 = time.time()
        if t1 > last_add_train + 0.7:
            train_samples.append(last_train_sample)
            print("RETRAINING")
            main_clf = RandomForestRegressor(100)
            X = [[labelize(y) if isinstance(y, str) else y for y in x[:-1]] for x in train_samples]
            y = [x[-1] for x in train_samples]
            X = ohe.fit_transform(X)
            y = np.array(y)
            main_clf.fit(X, y)
            print(train_samples)
            print("RETRAINING DONE")
            last_train_sample = None
            last_add_train = None
            last_add_train = t1


COMMANDS = {
    "add_train": add_train,
    "whereami.predict": p.predict,
    "display.get_average": d.get_average,
    "whereami.refresh": p.refresh
}

# timers in seconds
TIMERS = {
    "adjust_brightness": 0.3,
    "retrain": 0.05,
    "display.get_average": 0.3,
    "whereami.predict": 30,
    "whereami.refresh": 300,
}


def main():
    ctx = zmq.Context()
    poller = zmq.Poller()

    timers = ZmqTimerManager()
    timers.add_timer(ZmqTimer(TIMERS["display.get_average"], d.get_average))
    timers.add_timer(ZmqTimer(TIMERS["adjust_brightness"], adjust_brightness))
    timers.add_timer(ZmqTimer(TIMERS["retrain"], retrain))
    timers.add_timer(ZmqTimer(TIMERS["whereami.predict"], COMMANDS["whereami.predict"]))
    timers.add_timer(ZmqTimer(TIMERS["whereami.refresh"], COMMANDS["whereami.refresh"]))

    grabber = ctx.socket(zmq.PULL)
    grabber.connect("ipc:///tmp/screensy_socket")
    poller.register(grabber, zmq.POLLIN)

    while True:
        timers.check()
        next_interval = timers.get_next_interval()
        socks = dict(poller.poll(next_interval))
        for sock in socks:
            data = sock.recv().decode('utf-8')
            command, *args = data.split()
            if command in COMMANDS:
                fn = COMMANDS[command]
                fn(*args)
            else:
                print("RECEIVED unhandled: %s" % data)


if __name__ == "__main__":
    main()
