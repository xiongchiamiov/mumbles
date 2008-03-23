#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus

class GenericMumbles(MumblesInputPlugin):

	plugin_name = "GenericMumbler"

	dbus_interface = "org.mumblesproject.Mumbles"
	dbus_path = "/org/mumblesproject/Mumbles"

	def __init__(self, session_bus, options = None, verbose=False):
		self.signal_config = {
			"Notify": self.Notify
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)

	def Notify(self, title, msg):
		self.set_title(title)
		self.set_msg(msg)
		self.alert()

