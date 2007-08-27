#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
import gnomevfs
import os


class FirefoxMumbles(MumblesPlugin):

	plugin_name = "FirefoxMumbles"
	plugin_dir = "firefox"

	dbus_interface = "org.mozilla.firefox.DBus"
	dbus_path = "/org/mozilla/firefox/DBus"

	icons = {'firefox' : 'firefox.png'}

	__uri = None

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"DownloadComplete": self.DownloadComplete
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)
		self.add_click_handler(self.onClick)

 	def DownloadComplete(self, title, uri):
 		self.__uri = uri
 		uri = os.path.basename(uri)
		icon = self.get_icon('firefox')
 		self.mumbles_notify.alert(self.plugin_name, title, uri, icon)

 	def onClick(self, widget, event, plugin_name):
 		if event.button == 3:
 			self.mumbles_notify.close(widget.window)
 		else:
 			self.open_uri(self.__uri)

 	def open_uri(self, uri):
 		mime_type = gnomevfs.get_mime_type(uri)
 		application = gnomevfs.mime_get_default_application(mime_type)
 		os.system(application[2] + ' "' + uri + '" &')
