#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
import cgi

class ThunderbirdMumbles(MumblesPlugin):

	plugin_name = "ThunderbirdMumbles"
	dbus_interface = "org.mozilla.thunderbird.DBus"
	dbus_path = "/org/mozilla/thunderbird/DBus"

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"NewMail": self.NewMail
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)


	def NewMail(self, from_addr, subject):
		from_addr_clean = cgi.escape(from_addr)
		subject_clean = cgi.escape(subject)
		icon = self.plugin_dir+"/thunderbird/thunderbird/themes/thunderbird.png"

		self.mumbles_notify.alert(self.plugin_name, from_addr_clean, subject_clean, icon)

