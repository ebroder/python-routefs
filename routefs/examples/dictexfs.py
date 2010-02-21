#!/usr/bin/python


import routefs


class DictExFS(routefs.DictFS):
    files = dict(Hello='World',
                 Directory=dict(a='a', b='b', c=routefs.Symlink('a')))


if __name__ == '__main__':
    routefs.main(DictExFS)
