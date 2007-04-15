#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
        import dbus.glib


class GenericMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'GenericMumbler'
	__dbus_name__ = 'org.mumblesproject.Mumbles'

	dbus_interface = 'org.mumblesproject.Mumbles'
	dbus_object = '/org/mumblesproject/Mumbles'

	def Notify(self, name, message):
		# should be getting here - why not?
		icon = None
		self.mumbles_notify.alert(name, message, icon)

	def connect_signals(self):
		self.interface.connect_to_signal('Notify', self.Notify)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		try:
			mumbles_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(mumbles_object, self.dbus_interface)
			self.connect_signals()
			return True
		except:
			return False
