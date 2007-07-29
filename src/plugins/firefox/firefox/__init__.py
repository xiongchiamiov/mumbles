#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
        import dbus.glib
import cgi


class FirefoxMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'FirefoxMumbles'
	__dbus_name__ = "org.mozilla.firefox.DBus"

	dbus_interface = "org.mozilla.firefox.DBus"
	dbus_object = "/org/mozilla/firefox/DBus/DownloadComplete"


	def DownloadComplete(self, title, subject):
		title = cgi.escape(title)
		subject = cgi.escape(subject)
		icon = self.plugin_dir+"/firefox/firefox/themes/firefox.png"
		self.mumbles_notify.alert(title, subject, icon)


	def connect_signals(self):
		self.interface.connect_to_signal("DownloadComplete", self.DownloadComplete)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		try:
			firefox_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(firefox_object, self.dbus_interface)

			self.connect_signals()
			return True
		except:
			return False
