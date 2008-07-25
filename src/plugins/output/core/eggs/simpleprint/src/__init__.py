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

	def init_options(self):
		self.add_option(BooleanOption('advanced',
			False,
			'Advanced',
			'Print advanced details for the alert.'))

	def alert(self, alert_object):
		if self.get_option('advanced'):
			print "Plugin: %s" %alert_object.get_name()
			print "Title: %s" %alert_object.get_title()
			print "Message: %s" %alert_object.get_msg()
			print "Icon: %s\n" %alert_object.get_icon()
		else:
			print "%s\n" %(alert_object.to_string())
