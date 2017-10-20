import time
import zmq

import pandas as pd

from brightml.timer import ZmqTimer, ZmqTimerManager

from brightml.utils import save_sample

from brightml.features import p, d
from brightml.features import get_features
from brightml.brightness import BrightnessManager
from brightml.pipeline import get_classifier_pipeline

bm = BrightnessManager()
pipeline_clf = get_classifier_pipeline(None)
old_value = None

last_add_train = time.time()
last_train_sample = None


def adjust_brightness():
    global last_train_sample
    global old_value
    if last_train_sample is None and pipeline_clf is not None:
        features = get_features()
        new_value = (features["ambient_light"],
                     features["display_window_name"], features["datetime_hour"])
        if old_value != new_value:
            print("NEW STATE", features)
            if pipeline_clf:
                try:
                    #t1 = time.time()
                    data = pd.DataFrame([features])
                    pipeline, clf = pipeline_clf
                    data = pipeline.transform(data)
                    X, _ = data[:, :-1], data[:, -1]
                    pred = int(100 * clf.predict(X)[0])
                    # print("taken", time.time() - t1)
                    print("NEW BRIGHTNESS %", pred)
                    bm.set_by_percentage(pred)
                except ValueError as e:
                    print(e)
                    return
            else:
                print("PREDICTING!")
            old_value = new_value


def add_train(bright_change):
    global last_add_train
    global last_train_sample

    last_add_train = time.time()

    new_brightness = bm.get_percentage()
    features = get_features()
    features["new_brightness"] = new_brightness

    last_train_sample = features
    print("RECEIVED added training", last_train_sample)

    print("OK", bright_change)


def retrain():
    global last_train_sample
    global last_add_train
    global pipeline_clf
    if last_train_sample is not None:
        t1 = time.time()
        if t1 > last_add_train + 0.7:
            save_sample(last_train_sample)
            print("RETRAINING")
            pipeline_clf = get_classifier_pipeline(None)
            print("RETRAINING DONE")
            last_train_sample = None
            last_add_train = None
            last_add_train = t1


COMMANDS = {
    "add_train": add_train,
    "whereami.predict": p.predict,
    "display.get_window_info": d.get_window_info,
    "whereami.refresh": p.refresh
}

# timers in seconds
TIMERS = {
    "adjust_brightness": 0.3,
    "retrain": 0.05,
    "display.get_window_info": 0.3,
    "whereami.predict": 30,
    "whereami.refresh": 300,
}


def main():
    ctx = zmq.Context()
    poller = zmq.Poller()

    timers = ZmqTimerManager()
    timers.add_timer(ZmqTimer(TIMERS["display.get_window_info"], d.get_window_info))
    timers.add_timer(ZmqTimer(TIMERS["adjust_brightness"], adjust_brightness))
    timers.add_timer(ZmqTimer(TIMERS["retrain"], retrain))
    timers.add_timer(ZmqTimer(TIMERS["whereami.predict"], COMMANDS["whereami.predict"]))
    timers.add_timer(ZmqTimer(TIMERS["whereami.refresh"], COMMANDS["whereami.refresh"]))

    grabber = ctx.socket(zmq.PULL)
    grabber.connect("ipc:///tmp/brightml_socket")
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
