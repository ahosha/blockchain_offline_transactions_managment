from threading import Timer
import sys


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        try:
            self.is_running = False
            self.start()
            self.function(*self.args, **self.kwargs)
        except:
            e = sys.exc_info()[0]
            print('_run <p>Error: %s</p>' % e)
            pass

    def start(self):
        try:
            if not self.is_running:
                self._timer = Timer(self.interval, self._run)
                self._timer.start()
                self.is_running = True
        except:
            e = sys.exc_info()[0]
            print('start <p>Error: %s</p>' % e)
            pass

    def stop(self):
        self._timer.cancel()
        self.is_running = False