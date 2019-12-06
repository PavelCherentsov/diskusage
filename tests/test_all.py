import os
import shutil
import unittest
from math import inf
from pyfakefs import fake_filesystem_unittest
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from modules.diskusage import DiskUsage, File


class DiskUsageTest(unittest.TestCase):
    def setUp(self):
        os.mkdir('./tests/dir0')
        for i in range(1, 10):
            os.mkdir(f'./tests/dir0/dir{i}')
        for i in range(1, 10):
            for j in range(10, 20):
                os.mkdir(f'./tests/dir0/dir{i}/dir{j}')
        for i in range(1, 10):
            for j in range(10, 20):
                file = open(f".//tests/dir0/dir{i}/dir{j}/{i}{j}.ext{i % 2}",
                            "w")
                file.write('Test ')
                file.close()
        for i in range(1, 10):
            s = 'A'
            for j in range(10, 20):
                s += 'AA'
                file = open(f".//tests/dir0/dir{i}/dir{j}/{i}{j}.ext{i % 2}",
                            "a")
                file.write(s)
                file.close()

    def tearDown(self):
        shutil.rmtree('./tests/dir0/')

    def test_all_paths(self):
        du = DiskUsage('./tests/dir0/', inf, '*', '!*', True, False)
        du.start()
        du.res.sort(key=lambda x: x.size, reverse=True)
        self.assertEqual(len(du.res), 10 * 9 + 10 * 9 + 9 + 1)
        self.assertEqual(du.res[0].count, 10 * 9 + 10 * 9 + 9)
        self.assertEqual(du.res[-1].count, 1)

    def test_exclude(self):
        du = DiskUsage('./tests/dir0/', inf, '*', '*dir10*', False, False)
        du.start()
        self.assertEqual(len(du.res), 9 * 9 + 9 * 9 + 9 + 1)

    def test_pattern(self):
        du = DiskUsage('./tests/dir0/', inf, '*dir1/*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 10 + 10)
        du = DiskUsage('./tests/dir0/', inf, '*.*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 10 * 9 + 1)

    def test_level(self):
        du = DiskUsage('./tests/dir0/', 0, '*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 1)
        du = DiskUsage('./tests/dir0/', 1, '*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 1 + 9)
        du = DiskUsage('./tests/dir0/', 2, '*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 1 + 9 + 9 * 10)

    def test_stat_ext(self):
        du = DiskUsage('./tests/dir0/', inf, '*', '!*', False, True)
        du.start()
        self.assertEqual(len(list(du.res.keys())), 2)
        self.assertTrue('.ext1' in list(du.res.keys()))
        self.assertTrue('.ext0' in list(du.res.keys()))


class FileTest(unittest.TestCase):
    def test_file_size(self):
        f = File('/path', 0, 0, '')
        self.assertEqual(f.get_size(0), '0 B')
        f = File('/path', 0, 1024, '')
        self.assertEqual(f.get_size(1024), '1.0 KB')
        f = File('/path', 0, 1024 * 1024, '')
        self.assertEqual(f.get_size(1024 * 1024), '1.0 MB')
        f = File('/path', 0, 1024 * 1024 * 1024, '')
        self.assertEqual(f.get_size(1024 * 1024 * 1024), '1.0 GB')

    def test_file_path(self):
        f = File('\\path', 0, 0, '')
        self.assertEqual(f.path, '/path')

    def test_file_str(self):
        f = File('/path', 0, 1, '')
        f.set_histogram(1)
        self.assertEqual('0    1 B          [##########]          /path',
                         str(f))
        f = File('/path', 0, 0, '')
        f.set_histogram(0)
        self.assertEqual('0    0 B          [          ]          /path',
                         str(f))


class FakeTest(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()
        os.makedirs('/home/x/alpha')
        os.makedirs('/home/x/beta')
        with open('/home/x/p.conf', 'w') as f:
            f.write('foo')
        with open('/home/x/alpha/a.conf', 'w') as f:
            f.write('bar')

    def test_stats(self):
        du = DiskUsage('/home', inf, '*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 6)

    def test_symlink(self):
        os.symlink('/home/x', '/home/x/beta/x')
        os.symlink('/home/x', '/home/x/alpha/x')
        du = DiskUsage('/home', inf, '*', '!*', False, False)
        du.start()
        self.assertEqual(len(du.res), 8)

    def test_big_files(self):
        for i in range(1, 11):
            for j in range(1, 11):
                os.makedirs(f'/KEK/dir{i}/d{j}')
                for k in range(1, 11):
                    with open(f'/KEK/dir{i}/d{j}/file{k}.mp{k % 3}', 'w') as f:
                        f.write('0' * k)

        du = DiskUsage('/KEK', inf, '*', '!*', True, False)
        du.start()
        du.res.sort(key=lambda x: x.size, reverse=True)
        self.assertEqual(len(du.res), 1 + 10 + 10 * 10 + 10 * 10 * 10)

        du = DiskUsage('/KEK', 0, '*', '!*', True, False)
        du.start()
        du.res.sort(key=lambda x: x.size, reverse=True)
        self.assertEqual(len(du.res), 1)

        du = DiskUsage('/KEK', 1, '*', '!*', True, False)
        du.start()
        du.res.sort(key=lambda x: x.size, reverse=True)
        self.assertEqual(len(du.res), 1 + 10)

        du = DiskUsage('/KEK', 0, '*', '!*', True, False)
        du.start()
        self.assertEqual(du.res[0].count, 10 + 10 * 10 + 10 * 10 * 10)
        self.assertEqual(du.res[0].level, 0)

        du = DiskUsage('/KEK', inf, '*', '!*', True, True)
        du.start()
        self.assertEqual(len(list(du.res.values())), 3)


if __name__ == '__main__':
    unittest.main()
