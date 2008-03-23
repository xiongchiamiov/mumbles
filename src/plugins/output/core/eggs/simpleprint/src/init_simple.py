#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Default Mumbles Output Plugin
#
#------------------------------------------------------------------------

from MumblesOutputPlugin import *

class DefaultMumblesOutput(MumblesOutputPlugin):

	plugin_name = "DefaultMumblesOutput"

	def __init__(self, verbose=False):
		MumblesOutputPlugin.__init__(self, verbose)

	def get_name(self):
		return self.plugin_name

	def alert(self, alert_object):
		if self._verbose:
			print "Default output plugin alert!"
			print alert_object.to_string()
