#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Pidgin Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple pidgin plugin for mumbles'

setup(
	name='PidginMumbles',
	version='0.1',
	description=__doc__,
	author=__author__,
	packages=['pidgin'],
	entry_points='''
	[mumbles.plugins]
	Pidgin = pidgin:PidginMumbles
	'''
)

