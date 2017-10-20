import time


class ZmqTimerManager(object):
    def __init__(self):
        self.timers = []
        self.next_call = 0

    def add_timer(self, timer):
        self.timers.append(timer)

    def check(self):
        if time.time() > self.next_call:
            for timer in self.timers:
                timer.check()

    def get_next_interval(self):
        if time.time() >= self.next_call:
            call_times = []
            for timer in self.timers:
                call_times.append(timer.get_next_call())
            self.next_call = min(call_times)
            if self.next_call < time.time():
                val = 1
            else:
                val = (self.next_call - time.time()) * 1000
        else:
            val = (self.next_call - time.time()) * 1000
        if val < 1:
            val = 1
        return val


class ZmqTimer(object):
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.last_call = 0

    def check(self):
        if time.time() > (self.interval + self.last_call):
            self.callback()
            self.last_call = time.time()

    def get_next_call(self):
        return self.last_call + self.interval
