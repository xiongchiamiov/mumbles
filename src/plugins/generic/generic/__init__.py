#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus

class GenericMumbles(MumblesPlugin):

	plugin_name = "GenericMumbler"
	dbus_interface = "org.mumblesproject.Mumbles"
	dbus_path = "/org/mumblesproject/Mumbles"

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"Notify": self.Notify
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)

	def Notify(self, name, message):
		icon = None
		self.mumbles_notify.alert(name, message, icon)

