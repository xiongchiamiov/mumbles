#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# LibNotify Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import os
import dbus
import dbus.service

class LibNotifyServiceObject(dbus.service.Object):

	mumbles_plugin = None
	def __init__(self, bus, plugin):
		self.mumbles_plugin = plugin
		dbus.service.Object.__init__(self, bus, '/org/freedesktop/Notifications')

	@dbus.service.method(dbus_interface='org.freedesktop.Notifications', in_signature='susssasa{sv}i', out_signature='i')
	def Notify(self,app_name,replaces_id,app_icon,summary,body,actions,hints,expire_timeout):
		if not os.path.exists(app_icon):
			app_icon = ''
		self.mumbles_plugin.mumbles_notify.alert(app_name, summary, body, app_icon)
		return replaces_id

class LibNotifyMumbles(MumblesPlugin):

	plugin_name = "LibNotifyMumbles"

	dbus_iface =  'org.freedesktop.DBus'
	dbus_path =  '/org/freedesktop/DBus'

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {}
		MumblesPlugin.__init__(self, mumbles_notify, session_bus)

		proxy = session_bus.get_object(self.dbus_iface, self.dbus_path)
		iface= dbus.Interface(proxy,dbus_interface=self.dbus_iface)

		tmp = iface.RequestName('org.freedesktop.Notifications', 0)

		os.system("killall notification-daemon > /dev/null 2>&1")
		os.system("killall notify-osd > /dev/null 2>&1")

		self.service_object = LibNotifyServiceObject(session_bus, self)

