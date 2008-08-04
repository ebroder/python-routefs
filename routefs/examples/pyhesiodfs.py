#!/sw/bin/python2.5

import hesiod
import routefs
from routes import Mapper

class PyHesiodFS(routefs.RouteFS):
    def __init__(self, *args, **kwargs):
        super(PyHesiodFS, self).__init__(*args, **kwargs)
        
        self.cache = {}
    
    def make_map(self):
        m = Mapper()
        m.connect('', controller='getList')
        m.connect(':action', controller='getLocker')
        return m
    
    def getLocker(self, action):
        if action in self.cache:
            return routefs.Symlink(self.cache[action])
        
        try:
            filsys = hesiod.FilsysLookup(action).filsys[0]
            if filsys['type'] == 'AFS':
                self.cache[action] = filsys['location']
                return routefs.Symlink(self.cache[action])
        except (TypeError, KeyError, IndexError):
            return
    
    def getList(self, action):
        return routefs.Directory(self.cache.keys())

if __name__ == '__main__':
    routefs.main(PyHesiodFS)
