import os
from fnmatch import fnmatch
import filecmp


class File:
    def __init__(self, path, level, size, count):
        self.path = path.replace('\\', '/')
        self.level = level
        self.size = size
        self.histogram = '[          ]'
        self.count = count

    def __str__(self):
        return '%-5s%-13s%-15s%-7s%s' % (
            self.level, self.get_size(self.size), self.histogram,
            self.count, self.path)

    @staticmethod
    def get_size(size):
        if size >= 2 ** 30:
            return f'{round(size / 2 ** 30, 2)} GB'
        elif size >= 2 ** 20:
            return f'{round(size / 2 ** 20, 2)} MB'
        elif size >= 2 ** 10:
            return f'{round(size / 2 ** 10, 2)} KB'
        return f'{size} B'

    def set_histogram(self, total_size):
        count = 0
        if total_size != 0:
            count = int(round(self.size / total_size * 10))
        percent = '#' * count
        self.histogram = f'[{percent:>10}]'


class DiskUsage:
    def __init__(self, path, level, pattern, exclude, count_files, stat_ext, diff):
        self.path = path
        self.level = level
        self.count_files = count_files

        self.pattern = pattern
        self.exclude = exclude

        self.total_size = 0
        self.count = 0
        self.deleted_size = 0
        self.dif = diff

        if stat_ext:
            self.add = self.add_statistics
            self.res = {}
        elif diff:
            self.add = self.add_diff_files
            self.res = {}
            self.diff_files = []
        else:
            self.add = self.add_files
            self.res = []

    def start(self):
        size, count = self.go_in_dir(os.path.abspath(self.path), 0, 0)
        self.check_params_and_add(-1, self.path, size, count)
        if self.dif:
            print(str(self.count) + '\t' + File.get_size(self.total_size))

    def go_in_dir(self, root, level, size):
        res_size = 0
        count_files = 0
        for dirname in os.listdir(root):
            try:
                path = f'{root}/{dirname}'
                if os.path.isdir(path) and not os.path.islink(path):
                    size, count = self.go_in_dir(path, level + 1, size)
                    self.check_params_and_add(level, path, size, count)
                    res_size += size
                    count_files += count + 1
                else:
                    size = os.path.getsize(path)
                    self.check_params_and_add(level, path, size, '')
                    res_size += size
                    count_files += 1
            except Exception:
                pass
        return res_size, count_files

    def check_params_and_add(self, level, path, size, count):
        if self.level >= level + 1:
            if fnmatch(path, self.pattern) and not fnmatch(path, self.exclude):
                self.add(level, path, size, count)

    def add_statistics(self, level, path, size, count):
        if os.path.isfile(path):
            extension = os.path.splitext(path)[1]
            if extension not in self.res:
                self.res[extension] = File(extension, '', size, 1)
            else:
                self.res[extension].size += size
                self.res[extension].count += 1
            self.total_size = max(self.total_size, self.res[extension].size)

    def add_files(self, level, path, size, count):
        if self.count_files:
            self.res.append(File(path, level + 1, size, count))
        else:
            self.res.append(File(path, level + 1, size, ''))
        self.total_size = max(self.total_size, size)

    def add_diff_files(self, level, path, size, count):
        is_new_file = True
        if os.path.isfile(path):
            for e in self.diff_files:
                if filecmp.cmp(path, e):
                    print(e[len(self.path):]+"\t=======\t"+path[len(self.path):] + '\t' + File.get_size(os.path.getsize(path)))
                    self.total_size += os.path.getsize(path)
                    self.count += 1
                    os.remove(path)
                    is_new_file = False
                    break
            if is_new_file:
                self.diff_files.append(path)




