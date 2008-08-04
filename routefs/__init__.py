import fuse
import routes
import errno
import stat

fuse.fuse_python_api = (0, 2)

class RouteStat(fuse.Stat):
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

class RouteMeta(type):
    def __init__(cls, classname, bases, dict_):
        super(RouteMeta, cls).__init__(classname, bases, dict_)
        if bases != (fuse.Fuse,):
            new_funcs = set(dict_.keys()).difference(dir(RouteFS))
            cls.controllers([func for func in new_funcs \
                                 if not func.startswith('_')])

class RouteFS(fuse.Fuse):
    __metaclass__ = RouteMeta
    def __init__(self, *args, **kwargs):
        super(RouteFS, self).__init__(*args, **kwargs)
        
        self.map = self.make_map()
        self.map.create_regs(self.controller_list)
        
    def make_map(self):
        m = routes.Mapper()
        
        m.connect(':controller')
        
        return m
    
    @classmethod
    def controllers(cls, lst):
        cls.controller_list = lst
    
    def _get_file(self, path):
        match = self.map.match(path)
        if match is None:
            return
        controller = match.pop('controller')
        result = getattr(self, controller)(**match)
        return result
    
    def readdir(self, path, offset):
        obj = self._get_file(path)
        if type(obj) is not Directory:
            return
        else:
            for member in ['.', '..'] + obj:
                yield fuse.Direntry(str(member))
    
    def getattr(self, path):
        obj = self._get_file(path)
        if obj is None:
            return -errno.ENOENT
        
        st = RouteStat()
        if type(obj) is Directory:
            st.st_mode = stat.S_IFDIR | 0755
            st.st_nlink = 2
        elif type(obj) is Symlink:
            st.st_mode = stat.S_IFLNK | 0777
            st.st_nlink = 1
            st.st_size = len(obj)
        else:
            st.st_mode = stat.S_IFREG | 0444
            st.st_nlink = 1
            st.st_size = len(obj)
        
        return st
    
    def read(self, path, length, offset):
        obj = self._get_file(path)
        if obj is None:
            return -errno.ENOENT
        elif type(obj) in (Directory, Symlink):
            return -errno.EINVAL
        else:
            return obj[offset:offset + length]
    
    def readlink(self, path):
        obj = self._get_file(path)
        if type(obj) is not Symlink:
            return -errno.EINVAL
        else:
            return obj

class Directory(list):
    """
    A dummy class representing a filesystem entry that should be a
    directory
    """
    pass

class Symlink(str):
    """
    A dummy class representing something that should be a symlink
    """
    pass

def main(cls):
    server = cls(version="%prog " + fuse.__version__,
                 usage=fuse.Fuse.fusage,
                 dash_s_do='setsingle')
    server.parse(errex=1)
    server.main()
