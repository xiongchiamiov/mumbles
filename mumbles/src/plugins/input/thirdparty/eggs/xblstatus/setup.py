#------------------------
# A Mumbles Plugin for XBL Status
#   Copyright (c) 2008 Chris Hollenbeck <chris.hollenbeck@gmail.com>
#   Licensed under the GPL
#------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'chris.hollenbeck@gmail.com'
__doc__ = 'A XBL Status plugin for mumbles'
__version__ = '0.1'

setup (
    name = 'XBLStatusMumbles',
    version = __version__,
    description = __doc__,
    author = __author__,
    packages = ['xblstatus'],
    package_dir = {'xblstatus' : 'src'},
    entry_points = '''
    [mumbles.plugins]
    XBLStatus = xblstatus:XBLStatusMumbles
    '''
)

# copy egg file to plugin directory
copy("dist/XBLStatusMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

