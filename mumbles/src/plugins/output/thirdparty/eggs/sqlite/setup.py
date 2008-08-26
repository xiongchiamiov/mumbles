#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# SQLite Output Plugin
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A sqlite output plugin for mumbles'
__version__ = '0.1'

setup(
	name='SQLiteMumblesOutput',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['sqlite'],
	package_dir={'sqlite':'src'},
	entry_points='''
	[mumbles.plugins]
	SQLiteMumblesOutput = sqlite:SQLiteMumblesOutput
	'''
)

# copy egg file to plugin directory
copy("dist/SQLiteMumblesOutput-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")


