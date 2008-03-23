#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Gaim Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple gaim plugin for mumbles'
__version__ = '0.1'

setup(
	name='GaimMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['gaim'],
	package_dir={'gaim':'src'},
	package_data={'':['themes/firefox.png', 'themes/irc.png']},
	entry_points='''
	[mumbles.plugins]
	Gaim = gaim:GaimMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/GaimMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

