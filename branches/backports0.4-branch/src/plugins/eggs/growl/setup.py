#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Simple Growl Network Server Plugin
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple Growl network server plugin for mumbles'
__version__ = '0.1'

setup(
	name='GrowlMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['growl'],
	package_dir={'growl':'src'},
	entry_points='''
	[mumbles.plugins]
	GrowlMumbles = growl:GrowlMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/GrowlMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")


