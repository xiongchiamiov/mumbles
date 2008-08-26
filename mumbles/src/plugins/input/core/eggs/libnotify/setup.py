#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# libnotify Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple plugin for mumbles that listens for libnotify messages'
__version__ = '0.1'

setup(
	name='LibNotifyMumblesInput',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['libnotify'],
	package_dir={'libnotify':'src'},
	package_data={'':['themes/libnotify.png']},
	entry_points='''
	[mumbles.plugins]
	LibNotifyMumblesInput = libnotify:LibNotifyMumblesInput
	'''
)

# copy egg file to plugin directory
copy("dist/LibNotifyMumblesInput-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

