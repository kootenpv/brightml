# todo: chargedness of battery

import time
from datetime import datetime
import numpy as np

try:
    from whereami.predict import Predicter

    whereami_predicter = Predicter()
except ImportError:
    print("Could not load `whereami` module")
    whereami_predicter = None

from brightml.battery import get_battery_feature
from brightml.xdisplay import Display

d = Display()


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def get_ambient_light():
    try:
        # please, if your ambient light sensor doesn't work, post the path in the issues on github
        with open("/sys/bus/iio/devices/iio:device0/in_illuminance_input") as f:
            ambient = int(f.read())
            return ambient
    except:
        return np.nan


def get_time_features():
    now = datetime.strptime(time.strftime(DATE_FORMAT, time.localtime()), DATE_FORMAT)
    data = {
        "datetime_hour": now.hour,
        "datetime_timezone": str(now.tzinfo),
        "datetime_date": str(now.date()),
        "datetime_full": str(now),
    }
    return data


def get_features():
    if whereami_predicter is None:
        whereami_value = np.nan
    else:
        whereami_value = whereami_predicter.predicted_value or whereami_predicter.predict()
    data = {"ambient_light": get_ambient_light(), "whereami": whereami_value}
    data.update(get_time_features())
    data.update(d.last_value or d.get_window_info())
    data.update({"battery": get_battery_feature()})
    return data
