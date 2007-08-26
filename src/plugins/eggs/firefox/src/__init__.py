#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
import cgi
import gnomevfs
import os


class FirefoxMumbles(MumblesPlugin):

	plugin_name = "FirefoxMumbles"
	dbus_interface = "org.mozilla.firefox.DBus"
	dbus_path = "/org/mozilla/firefox/DBus"

	__uri = None

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"DownloadComplete": self.DownloadComplete
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)
		self.addClickHandler(self.onClick)

 	def DownloadComplete(self, title, uri):
 		self.__uri = uri
 		title = cgi.escape(title)
 		uri = cgi.escape(os.path.basename(uri))
 		icon = self.plugin_dir+"/eggs/firefox/src/themes/firefox.png"
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
