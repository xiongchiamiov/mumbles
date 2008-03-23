#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Simple Growl Network Server Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus

class GrowlMumbles(MumblesInputPlugin):

	plugin_name = "GrowlMumbler"

	dbus_interface = "info.growl.Growl"
	dbus_path = "/info/growl/Growl"

	def __init__(self, session_bus, options = None, verbose = False):
		self.signal_config = {
			"Notify": self.Notify
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)

	def Notify(self, title, msg):
		self.set_title(title)
		self.set_msg(msg)
		self.alert()

