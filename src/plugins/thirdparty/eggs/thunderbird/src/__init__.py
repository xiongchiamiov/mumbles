#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus

class ThunderbirdMumbles(MumblesPlugin):

	plugin_name = "ThunderbirdMumbles"

	dbus_interface = "org.mozilla.thunderbird.DBus"
	dbus_path = "/org/mozilla/thunderbird/DBus"

	icons = {'thunderbird' : 'thunderbird.png'}

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"NewMail": self.NewMail
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)


	def NewMail(self, from_addr, subject):
		icon = self.get_icon('thunderbird')
		self.mumbles_notify.alert(self.plugin_name, from_addr, subject, icon)

