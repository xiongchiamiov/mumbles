#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Gaim Mumbles Plugin 
#
#------------------------------------------------------------------------

from setuptools import setup

__author__ = 'dot_j <dot_j@mumbles-project.org>'
__doc__ = 'A simple gaim plugin for mumbles'

setup(
	name='GaimMumbles',
	version='0.1',
	description=__doc__,
	author=__author__,
	packages=['gaim'],
	entry_points='''
	[mumbles.plugins]
	Gaim = gaim:GaimMumbles
	'''
)

