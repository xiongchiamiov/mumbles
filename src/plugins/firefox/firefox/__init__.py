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
import gnomevfs
import os


class FirefoxMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'FirefoxMumbles'
	__dbus_name__ = "org.mozilla.firefox.DBus"

	dbus_interface = "org.mozilla.firefox.DBus"
	dbus_object = "/org/mozilla/firefox/DBus/DownloadComplete"

	__uri = None

	def DownloadComplete(self, title, uri):
		self.__uri = uri
		title = cgi.escape(title)
		uri = cgi.escape(uri)
		icon = self.plugin_dir+"/firefox/firefox/themes/firefox.png"
		self.mumbles_notify.alert(title, uri, icon)

	def onClick(self, widget, event):
		if event.button == 3:
			self.mumbles_notify.close()
		else:
			self.open_uri(self.__uri)


	def connect_signals(self):
		self.interface.connect_to_signal("DownloadComplete", self.DownloadComplete)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		self.mumbles_notify.addClickHandler(self.onClick)

		try:
			firefox_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(firefox_object, self.dbus_interface)

			self.connect_signals()
			return True
		except:
			return False

	def open_uri(self, uri):
		mime_type = gnomevfs.get_mime_type(uri)
		application = gnomevfs.mime_get_default_application(mime_type)
		os.system(application[2] + ' "' + uri + '" &') 
