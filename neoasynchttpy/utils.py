from timeit import default_timer


class Timer(object):
    elapsed = 0

    def __str__(self):
        return self.elapsed

    def __enter__(self):
        self.start = default_timer()
        return self

    def __exit__(self, *args):
        end = default_timer()
        self.elapsed_secs = end - self.start
        self.elapsed = self.elapsed_secs * 1000
