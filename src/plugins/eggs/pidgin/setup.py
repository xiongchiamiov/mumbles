#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Pidgin Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple pidgin plugin for mumbles'
__version__ = '0.2'

setup(
	name='PidginMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['pidgin'],
	package_dir={'pidgin':'src'},
	package_data={'':['themes/pidgin.png', 'themes/irc.png']},
	entry_points='''
	[mumbles.plugins]
	Pidgin = pidgin:PidginMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/PidginMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

