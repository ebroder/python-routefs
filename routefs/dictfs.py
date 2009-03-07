"""
DictFS allows you to easily create read-only filesystems when the
file tree is known in advance.

To create your own DictFS descendent, simply override the files
property, which can be created either using the property
decorator, or just a simple assignment.

A dictionary represents a directory, with keys corresponding to
file names and the values corresponding to the file contents.
"""

import routefs
from routes import Mapper
import os

class DictFS(routefs.RouteFS):
    controllers = ['handler']
    
    @property
    def files(self):
        """
        This property should be overridden in your DictFS descendant
        """
        return dict()
    
    def make_map(self):
        m = Mapper()
        
        m.connect('*path', controller='handler')
        
        return m
    
    def handler(self, path, **kwargs):
        if path != '':
            elements = path.split(os.path.sep)
        else:
            elements = []
        
        try:
            tree = self.files
            for elt in elements:
                tree = tree[elt]
        except KeyError:
            return
        
        if type(tree) is dict:
            return tree.keys()
        else:
            return tree
