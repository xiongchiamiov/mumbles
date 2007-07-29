#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple Thunderbird new mail plugin for mumbles. Requires Thunderbird DBus Notification Extension (See README.txt)'

setup(
	name='ThunderbirdMumbles',
	version='0.1',
	description=__doc__,
	author=__author__,
	packages=['thunderbird'],
	entry_points='''
	[mumbles.plugins]
	Thunderbird = thunderbird:ThunderbirdMumbles
	'''
)

