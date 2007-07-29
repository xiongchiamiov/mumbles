#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Thunderbird Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
        import dbus.glib
import cgi


class ThunderbirdMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'ThunderbirdMumbles'
	__dbus_name__ = "org.mozilla.thunderbird.DBus"

	dbus_interface = "org.mozilla.thunderbird.DBus"
	dbus_object = "/org/mozilla/thunderbird/DBus/NewMail"


	def NewMail(self, from_addr, subject):
		from_addr_clean = cgi.escape(from_addr)
		subject_clean = cgi.escape(subject)
		icon = self.plugin_dir+"/thunderbird/thunderbird/themes/thunderbird.png"
		self.mumbles_notify.alert(from_addr_clean, subject_clean, icon)


	def connect_signals(self):
		self.interface.connect_to_signal("NewMail", self.NewMail)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		try:
			thunderbird_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(thunderbird_object, self.dbus_interface)

			self.connect_signals()
			return True
		except:
			return False
