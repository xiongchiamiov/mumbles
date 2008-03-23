#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Shell
# Plugins extend this class to define their own call backs
#
#------------------------------------------------------------------------

from MumblesPlugin import *

class MumblesOutputPlugin(MumblesPlugin):

	def __init__(self, options=None, verbose=False):
		MumblesPlugin.__init__(self, options, verbose)

	def alert(self):
		pass
