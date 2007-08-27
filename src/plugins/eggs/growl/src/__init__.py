#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Simple Growl Network Server Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus

class GrowlMumbles(MumblesPlugin):

	plugin_name = "GrowlMumbler"

	dbus_interface = "info.growl.Growl"
	dbus_path = "/info/growl/Growl"

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"Notify": self.Notify
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)

	def Notify(self, name, message):
		icon = None
		self.mumbles_notify.alert(self.plugin_name, name, message, icon)

