#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# LibNotify Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import os
import dbus
import dbus.service

class LibNotifyServiceObject(dbus.service.Object):

	mumbles_plugin = None
	def __init__(self, bus, plugin):
		self.mumbles_plugin = plugin
		dbus.service.Object.__init__(self, bus, '/org/freedesktop/Notifications')

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='susssasa{sv}i', out_signature='')
	def Notify(self,app_name,replaces_id,app_icon,summary,body,actions,hints,expire_timeout):
		self.mumbles_plugin.set_title(app_name+" "+summary)
		self.mumbles_plugin.set_msg(body)
		self.mumbles_plugin.alert()
		return

class LibNotifyMumblesInput(MumblesInputPlugin):

	plugin_name = "LibNotifyMumblesInput"

	dbus_iface =  'org.freedesktop.DBus'
	dbus_path =  '/org/freedesktop/DBus'

	def __init__(self, session_bus, options=None, verbose=False):
		MumblesInputPlugin.__init__(self, session_bus, options, verbose)

		proxy = session_bus.get_object(self.dbus_iface, self.dbus_path)
		iface= dbus.Interface(proxy,dbus_interface=self.dbus_iface)

		tmp = iface.RequestName('org.freedesktop.Notifications', 0)

		os.system("killall notification-daemon > /dev/null 2>&1")

		self.service_object = LibNotifyServiceObject(session_bus, self)

