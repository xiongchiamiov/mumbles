#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles DBus Handler
#
#------------------------------------------------------------------------

from MumblesGlobals import *
import dbus
import dbus.service

class MumblesDBus(dbus.service.Object):
	def __init__(self,bus_name):
		dbus.service.Object.__init__(self,bus_name,MUMBLES_DBUS_OBJECT)

	@dbus.service.signal(dbus_interface=MUMBLES_DBUS_INTERFACE, signature='ss')
	def Notify(self, title, message):
		pass

class MumblesPluginDBus(dbus.service.Object):
	def __init__(self,bus_name, path):
		dbus.service.Object.__init__(self,bus_name, path)

	@dbus.service.signal(dbus_interface=MUMBLES_DBUS_INTERFACE, signature='')
	def SentNotification(self):
		pass

	@dbus.service.signal(dbus_interface=MUMBLES_DBUS_INTERFACE, signature='')
	def ReceivedNotification(self):
		pass
