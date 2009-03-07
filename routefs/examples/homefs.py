#!/usr/bin/python
"""
RouteFS Example: HomeFS

If you work on a system where home directories are on network storage
(i.e. not in /home), mount HomeFS on /home. It's an automounter that
will automatically create symlinks from user -> their homedir whenever
/home/user is accessed in any way.
"""

import pwd
import routefs
from routes import Mapper

class HomeFS(routefs.RouteFS):
    controllers = ['getList', 'getUser']
    def __init__(self, *args, **kwargs):
        super(HomeFS, self).__init__(*args, **kwargs)
        self.cache = {}
    
    def make_map(self):
        m = Mapper()
        m.connect('', controller='getList')
        m.connect(':action', controller='getUser')
        return m
    
    def getUser(self, action, **kwargs):
        try:
            if action not in self.cache:
                self.cache[action] = pwd.getpwnam(action).pw_dir
            return routefs.Symlink(self.cache[action])
        except KeyError:
            return
    
    def getList(self, **kwargs):
        return self.cache.keys()

if __name__ == '__main__':
    routefs.main(HomeFS)
