import time
import asyncio

import pandas as pd


from brightml.features import p, d, get_features
from brightml.utils import save_sample
from brightml.brightness import BrightnessManager
from brightml.pipeline import get_classifier_pipeline
from brightml.file_watcher import watch_fs

try:
    # ensure_future() has been introduced in Python 3.4.4
    from asyncio import ensure_future
except ImportError:
    from asyncio import async as ensure_future


class Brightml():
    def __init__(self, display):
        self.old_value = None
        self.bm = BrightnessManager()
        self.display = display
        self.pipeline_clf = get_classifier_pipeline(None)

    def adjust_brightness(self):
        if self.pipeline_clf is not None:
            features = get_features()
            new_value = (features["ambient_light"],
                         features["display_window_name"], features["datetime_hour"])
            if self.old_value != new_value:
                #print("NEW STATE", features)
                if self.pipeline_clf:
                    #t1 = time.time()
                    data = pd.DataFrame([features])
                    pipeline, clf = self.pipeline_clf
                    if pipeline is None:
                        print(
                            "Change your brightness to create your first data sample (there is no data found).")
                        return
                    data = pipeline.transform(data)
                    # y is nans in this case
                    X, _ = data[:, :-1], data[:, -1]
                    pred = int(100 * clf.predict(X)[0])
                    tmpl = "new_brightness={}% app={}"
                    print(tmpl.format(pred, features["display_window_class"]))
                    self.bm.set_by_percentage(pred)
                else:
                    print("PREDICTING!")
                self.old_value = new_value

    async def retrain(self):
        await asyncio.sleep(0.7)
        features = get_features()
        features["new_brightness"] = self.bm.get_percentage()
        save_sample(features)
        print("RETRAINING")
        self.pipeline_clf = get_classifier_pipeline(None)
        print("RETRAINING DONE")
        self.adjust_brightness()


async def whereami():
    p.predict()
    await asyncio.sleep(30)
    ensure_future(whereami())


def main():
    bml = Brightml(d)
    from threading import Thread
    t = Thread(target=d.main_thread_fn, args=[bml.adjust_brightness])
    t.start()
    loop = asyncio.get_event_loop()
    if p is not None:
        loop.create_task(whereami())
    loop.run_until_complete(watch_fs(bml))
    t.join()


if __name__ == "__main__":
    main()
