#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus

class ThunderbirdMumbles(MumblesInputPlugin):

	plugin_name = "ThunderbirdMumbles"

	dbus_interface = "org.mozilla.thunderbird.DBus"
	dbus_path = "/org/mozilla/thunderbird/DBus"

	icons = {'thunderbird' : 'thunderbird.png'}

	def __init__(self, session_bus, options=None, verbose=False):
		self.signal_config = {
			"NewMail": self.NewMail
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)


	def NewMail(self, from_addr, subject):
		self.set_title(from_addr)
		self.set_msg(subject)
		self.set_icon('thunderbird')
		self.alert()

