#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Twitter Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
#import gnomevfs
#import os

class TwitterMumbles(MumblesPlugin):

	plugin_name = "TwitterMumbles"

	dbus_interface = "com.twitter.DBus"
	dbus_path = "/com/twitter/DBus"

	icons = {'twitter' : 'twitter.png'}

	__url = None

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"Notify": self.Notify,
			"NotifyNum": self.NotifyNum
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)
		self.add_click_handler(self.onClick)

 	def NotifyNum(self, num):
 		self.__url = 'http://twitter.com/home'
		icon = self.get_icon('twitter')
		title = "Twitter"
		msg = str(num)+" new messages!"
 		self.mumbles_notify.alert(self.plugin_name, title, msg, icon)

 	def Notify(self, id, created, relative_create, name, screen_name, text):
 		self.__url = 'http://twitter.com/'+screen_name+'/statuses/'+str(id)
		icon = self.get_icon('twitter')
		name = name+" ("+relative_create+")"
 		self.mumbles_notify.alert(self.plugin_name, name, text, icon)

 	def onClick(self, widget, event, plugin_name):
 		if event.button == 3:
 			self.mumbles_notify.close(widget.window)
 		else:
 			self.open_url(self.__url)

 	def open_url(self, url):
		print url
 		#mime_type = gnomevfs.get_mime_type(url)
 		#application = gnomevfs.mime_get_default_application(mime_type)
 		#os.system(application[2] + ' "' + url + '" &')
