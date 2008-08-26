#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Default Mumbles Output Plugin (on-screen popups)
#
#------------------------------------------------------------------------

from setuptools import setup
import sys, os
from shutil import copy

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple print to command line output plugin for mumbles'
__version__ = '0.1'

setup(
	name='SimplePrintMumblesOutput',
	version=__version__,
	description=__doc__,
	author=__author__,
	packages=['simpleprint'],
	package_dir={'simpleprint':'src'},
	entry_points='''
	[mumbles.plugins]
	SimplePrintMumblesOutput = simpleprint:SimplePrintMumblesOutput
	'''
)

# copy egg file to plugin directory
copy("dist/SimplePrintMumblesOutput-%s-py%d.%d.egg" %(__version__,sys.version_info[0],sys.version_info[1]), "../../")

