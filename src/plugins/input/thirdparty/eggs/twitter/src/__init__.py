#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Twitter Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus
#import gnomevfs
#import os

class TwitterMumbles(MumblesInputPlugin):

	plugin_name = "TwitterMumbles"

	dbus_interface = "com.twitter.DBus"
	dbus_path = "/com/twitter/DBus"

	icons = {'twitter' : 'twitter.png'}

	__url = None

	def __init__(self, session_bus, options = None, verbose=False):
		self.signal_config = {
			"Notify": self.Notify,
			"NotifyNum": self.NotifyNum
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)
		self.add_click_handler(self.onClick)

 	def NotifyNum(self, num):
 		self.__url = 'http://twitter.com/home'
		self.set_title("Twitter")
		self.set_msg(str(num)+" new messages!")
		self.set_icon('twitter')
 		self.alert()

 	def Notify(self, id, created, relative_create, name, screen_name, text):
 		self.__url = 'http://twitter.com/'+screen_name+'/statuses/'+str(id)
		self.set_title(name)
		self.set_msg("("+relative_create+")\n"+text)
		self.set_icon('twitter')
 		self.alert()

 	def onClick(self, widget, event, plugin_name):
 		self.open_url(self.__url)

 	def open_url(self, url):
		print url
 		#mime_type = gnomevfs.get_mime_type(url)
 		#application = gnomevfs.mime_get_default_application(mime_type)
 		#os.system(application[2] + ' "' + url + '" &')
