#!/usr/bin/python


import hesiod
from routes import Mapper

import routefs


class PyHesiodFS(routefs.RouteFS):
    controllers = ['getList', 'getReadme', 'getLocker']
    def __init__(self, *args, **kwargs):
        super(PyHesiodFS, self).__init__(*args, **kwargs)
        self.fuse_args.add("allow_other", True)

        self.cache = {}

    def make_map(self):
        m = Mapper()
        m.connect('/', controller='getList')
        m.connect('/README.txt', controller='getReadme')
        m.connect('/{action}', controller='getLocker')
        return m

    def getLocker(self, action, **kwargs):
        if action in self.cache:
            return routefs.Symlink(self.cache[action])

        try:
            filsys = hesiod.FilsysLookup(action).filsys[0]
            if filsys['type'] == 'AFS':
                self.cache[action] = filsys['location']
                return routefs.Symlink(self.cache[action])
        except (TypeError, KeyError, IndexError):
            return

    def getList(self, **kwargs):
        return self.cache.keys() + ['README.txt']

    def getReadme(self, **kwargs):
        return """
This is the pyHesiodFS FUSE automounter. To access a Hesiod filsys,
just access /mit/name.

If you're using the Finder, try pressing Cmd+Shift+G and then entering
/mit/name
"""


if __name__ == '__main__':
    routefs.main(PyHesiodFS)
