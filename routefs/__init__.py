"""
RouteFS is a base class for developing read-only FUSE filesystems that
lets you focus on the directory tree instead of the system calls.

RouteFS uses the Routes library developed for Pylons. URLs were
inspired by filesystems, and now you can have filesystems inspired by
URLs.
"""

import fuse
import routes
import errno
import stat

fuse.fuse_python_api = (0, 2)

class RouteStat(fuse.Stat):
    """
    RouteStat is a descendent of fuse.Stat, defined to make sure that
    all of the necessary attributes are always defined
    """
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class RouteFS(fuse.Fuse):
    """
    RouteFS: Web 2.0 for filesystems
    
    Any method that will be used as the controller in a Routes mapping
    (either by explicitly specifying the controller or by using the
    ':controller' variable) must be added to RouteFS.controllers
    """
    controllers = []
    def __init__(self, *args, **kwargs):
        super(RouteFS, self).__init__(*args, **kwargs)
        
        self.map = self.make_map()
        self.map.create_regs(self.controllers)
        
    def make_map(self):
        """
        This method should be overridden by descendents of RouteFS to
        define the routing for the filesystem
        """
        m = routes.Mapper()
        
        m.connect(':controller')
        
        return m
    
    def _get_file(self, path):
        """
        Find the filesystem entry object for a given path
        """
        match = self.map.match(path)
        if match is None:
            return NoEntry()
        controller = match.pop('controller')
        result = getattr(self, controller)(**match)
        if result is None:
            return NoEntry()
        if type(result) is str:
            result = File(result)
        if type(result) is list:
            result = Directory(result)
        return result
    
    def __getattr__(self, attr):
        """
        If the requested attribute is one of the standard FUSE op,
        return a function which finds the file matching the requested
        path, and passes the op to the object corresponding to that
        file.
        """
        def op(path, *args):
            file = self._get_file(path)
            if hasattr(file, attr) and callable(getattr(file, attr)):
                return getattr(file, attr)(*args)
            else:
                return -errno.EINVAL
        
        if attr in ['getattr', 'readlink', 'readdir', 'mknod', 'mkdir',
                    'unlink', 'rmdir', 'symlink', 'rename', 'link', 'chmod',
                    'chown', 'truncate', 'utime', 'open', 'read',
                    'write', 'release', 'fsync', 'flush', 'getxattr',
                    'listxattr', 'setxattr', 'removexattr']:
            return op
        else:
            raise AttributeError, attr
    
class TreeKey(object):
    def getattr(self):
        return -errno.EINVAL
    def readdir(self, offset):
        return -errno.EINVAL
    def read(self, length, offset):
        return -errno.EINVAL
    def readlink(self):
        return -errno.EINVAL
    def write(self, length, offset):
        return -errno.EINVAL

class NoEntry(TreeKey):
    def getattr(self):
        return -errno.ENOENT
    def readdir(self, offset):
        return -errno.ENOENT
    def read(self, length, offset):
        return -errno.ENOENT
    def readlink(self):
        return -errno.ENOENT
    def write(self, length, offset):
        return -errno.ENOENT

class TreeEntry(TreeKey):
    default_mode = 0444
    
    def __new__(cls, contents, mode=None):
        return super(TreeEntry, cls).__new__(cls, contents)
    
    def __init__(self, contents, mode=None):
        if mode is None:
            self.mode = self.default_mode
        else:
            self.mode = mode
        
        super(TreeEntry, self).__init__(contents)

class Directory(TreeEntry, list):
    """
    A dummy class representing a filesystem entry that should be a
    directory
    """
    default_mode = 0555

    def getattr(self):
        st = RouteStat()
        st.st_mode = stat.S_IFDIR | self.mode
        st.st_nlink = 2
        return st

    def readdir(self, offset):
        for member in ['.', '..'] + self:
            yield fuse.Direntry(str(member))

class Symlink(TreeEntry, str):
    """
    A dummy class representing something that should be a symlink
    """
    default_mode = 0777

    def getattr(self):
        st = RouteStat()
        st.st_mode = stat.S_IFLNK | self.mode
        st.st_nlink = 1
        st.st_size = len(self)
        return st

    def readlink(self):
        return self

class File(TreeEntry, str):
    """
    A dummy class representing something that should be a file
    """
    default_mode = 0444

    def getattr(self):
        st = RouteStat()
        st.st_mode = stat.S_IFREG | self.mode
        st.st_nlink = 1
        st.st_size = len(self)
        return st

    def read(self, length, offset):
        return self[offset:offset + length]

def main(cls):
    """
    A convenience function for initializing a RouteFS filesystem
    """
    server = cls(version="%prog " + fuse.__version__,
                 usage=fuse.Fuse.fusage,
                 dash_s_do='setsingle')
    server.parse(values=server, errex=1)
    server.main()

from dictfs import DictFS

__all__ = ['RouteFS', 'DictFS', 'Symlink', 'Directory', 'File', 'main']
