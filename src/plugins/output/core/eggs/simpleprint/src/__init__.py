#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# SimplePrint Mumbles Output Plugin
#
#------------------------------------------------------------------------

from MumblesOutputPlugin import *

class SimplePrintMumblesOutput(MumblesOutputPlugin):

	plugin_name = "SimplePrintMumblesOutput"

	def __init__(self, session_bus, options=None, verbose=False):
		MumblesOutputPlugin.__init__(self, session_bus, options, verbose)

	def get_name(self):
		return self.plugin_name

	def alert(self, alert_object):
		print alert_object.to_string()
