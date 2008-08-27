#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Plugin
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'aegis <lunixbochs@gmail.com>'
__doc__ = 'A core function plugin for mumbles'
__version__ = '0.1'

setup(
	name='CoreFuncMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['corefunc'],
	package_dir={'corefunc':'src'},
	entry_points='''
	[mumbles.plugins]
	CoreFuncMumbles = corefunc:CoreFuncMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/CoreFuncMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")


