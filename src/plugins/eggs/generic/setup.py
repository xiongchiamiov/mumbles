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

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A default plugin for mumbles'
__version__ = '0.1'

setup(
	name='GenericMumbles',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['generic'],
	package_dir={'generic':'src'},
	entry_points='''
	[mumbles.plugins]
	GenericMumbles = generic:GenericMumbles
	'''
)

# copy egg file to plugin directory
copy("dist/GenericMumbles-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")


