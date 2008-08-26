#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Twitter Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple twitter plugin for mumbles. Requires Twitter DBus Notification Script (See README)'
__version__ = '0.1'

setup(
	name='TwitterMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['twitter'],
	package_dir={'twitter':'src'},
	package_data={'':['themes/twitter.png']},
	entry_points='''
	[mumbles.plugins]
	Twitter = twitter:TwitterMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/TwitterMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

