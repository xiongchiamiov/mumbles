#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Shell
# Plugins extend this class to define their own call backs
#
#------------------------------------------------------------------------

from MumblesGlobals import *

class MumblesPlugin(object):

		plugin_name = ''
		dbus_interface = ''
		dbus_path = ''

		signal_confg = {}

		def __init__(self, mumbles_notify, session_bus):
			self.plugin_dir = PLUGIN_DIR

			self.mumbles_notify = mumbles_notify
			self.session_bus = session_bus

			for signal, call_back in self.signal_config.items():
				self.session_bus.add_signal_receiver(
					handler_function = call_back,
					signal_name = signal,
					dbus_interface = self.dbus_interface,
					path = self.dbus_path)

		def get_name(self):
			return self.plugin_name

		def addClickHandler(self, handler):
			self.mumbles_notify.addClickHandler(handler)
