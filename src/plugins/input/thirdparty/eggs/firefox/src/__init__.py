#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Firefox Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus
import gnomevfs
import os


class FirefoxMumbles(MumblesInputPlugin):

	plugin_name = "FirefoxMumbles"

	dbus_interface = "org.mozilla.firefox.DBus"
	dbus_path = "/org/mozilla/firefox/DBus"

	icons = {'firefox' : 'firefox.png'}

	__uri = None

	def __init__(self, session_bus, options=None, verbose=False):
		self.signal_config = {
			"DownloadComplete": self.DownloadComplete
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)
		self.add_click_handler(self.onClick)

 	def DownloadComplete(self, title, uri):
 		self.__uri = uri
 		uri = os.path.basename(uri)

		self.set_title(title)
		self.set_msg(uri)
		self.set_icon('firefox')
 		self.alert()

 	def onClick(self, widget, event, plugin_name):
		# to-do: make clikc handler work again
		pass

		'''
 		if event.button == 3:
 			self.mumbles_notify.close(widget.window)
 		else:
 			self.open_uri(self.__uri)
		'''

 	def open_uri(self, uri):
 		mime_type = gnomevfs.get_mime_type(uri)
 		application = gnomevfs.mime_get_default_application(mime_type)
 		os.system(application[2] + ' "' + uri + '" &')
