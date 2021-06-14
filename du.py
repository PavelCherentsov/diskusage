import argparse
from modules.diskusage import DiskUsage
from math import inf
from modules.Console import Console
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DISK USAGE')
    parser.add_argument('path', type=str,
                        help='Start directory where the scan starts')
    parser.add_argument('--level', '-l', metavar='N', type=int, default=inf,
                        help='Nesting limit')
    parser.add_argument('--sort', '-s', type=str,
                        choices=['name', 'size', 'level'],
                        default='name', help='Output sorting')
    parser.add_argument('--show-only', '-p', metavar='PATTERN', type=str,
                        default='*',
                        help='Sets the mask for directories and files')
    parser.add_argument('--exclude', '-x', metavar='PATTERN', type=str,
                        default='!*',
                        help='Excludes mask for directories and files')
    parser.add_argument('--stat-ext', '-e', action='store_true',
                        help='Mode: statistics on files of a certain '
                             'extension')
    parser.add_argument('--count-files', '-c', action='store_true',
                        help='Adds additional statistics (without --stat-ext)')
    parser.add_argument('--diff', '-d', action='store_true',
                        help='')
    args = parser.parse_args()
    try:
        Console(DiskUsage, args)
    except Exception as ex:
        print(str(ex), file=sys.stderr)
        sys.exit(1)
