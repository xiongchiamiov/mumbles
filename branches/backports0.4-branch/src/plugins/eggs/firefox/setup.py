#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple firefox download completion plugin for mumbles. Requires Firefox DBus Notification Extension (See README)'
__version__ = '0.1'

setup(
	name='FirefoxMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['firefox'],
	package_dir={'firefox':'src'},
	package_data={'':['themes/firefox.png']},
	entry_points='''
	[mumbles.plugins]
	Firefox = firefox:FirefoxMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/FirefoxMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

