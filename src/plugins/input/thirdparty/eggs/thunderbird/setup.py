#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple Thunderbird new mail plugin for mumbles. Requires Thunderbird DBus Notification Extension (See README)'
__version__ = '0.1'

setup(
	name='ThunderbirdMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['thunderbird'],
	package_dir={'thunderbird':'src'},
	package_data={'':['themes/thunderbird.png']},
	entry_points='''
	[mumbles.plugins]
	Thunderbird = thunderbird:ThunderbirdMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/ThunderbirdMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

