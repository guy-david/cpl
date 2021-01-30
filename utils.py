#!/usr/bin/env python3

import sys
import contextlib


@contextlib.contextmanager
def smart_open(file_path, mode):
    if file_path != '-':
        f = open(file_path, mode)
    elif 'r' in mode:
        f = sys.stdin
    else:
        f = sys.stdout

    try:
        yield f
    finally:
        if f not in [sys.stdin, sys.stdout]:
            f.close()
