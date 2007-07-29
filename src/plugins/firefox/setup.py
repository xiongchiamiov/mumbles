#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple firefox download completion plugin for mumbles. Requires Firefox DBus Notification Extension (See README.txt)'

setup(
	name='FirefoxMumbles',
	version='0.1',
	description=__doc__,
	author=__author__,
	packages=['firefox'],
	entry_points='''
	[mumbles.plugins]
	Firefox = firefox:FirefoxMumbles
	'''
)

