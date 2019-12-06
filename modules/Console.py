import signal
import sys


class Console:
    def __init__(self, du, args):
        self.du = du(args.path, args.level, args.show_only,
                     args.exclude, args.count_files, args.stat_ext)
        self.sort = args.sort
        self.stat_ext = args.stat_ext
        signal.signal(signal.SIGINT, self.stop)
        self.du.start()
        self.print()

    def print(self):
        if self.stat_ext:
            res = list(self.du.res.values())
        else:
            res = self.du.res

        if self.sort == 'name':
            res.sort(key=lambda x: x.path)
        if self.sort == 'size':
            res.sort(key=lambda x: x.size, reverse=True)
        if self.sort == 'level':
            res.sort(key=lambda x: x.level)

        for e in res:
            e.set_histogram(self.du.total_size)
            print(e)

    def stop(self, sig, frame):
        self.print()
        sys.exit(1)
