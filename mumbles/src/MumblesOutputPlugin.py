#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Shell
# Plugins extend this class to define their own call backs
#
#------------------------------------------------------------------------

from MumblesPlugin import *

class MumblesOutputPlugin(MumblesPlugin):

	dbus_interface = ''
	dbus_path = ''

	icons = {}
	signal_config = {}

	def __init__(self, session_bus, options=None, verbose=False):

		self.session_bus = session_bus

		for signal, call_back in self.signal_config.items():
				self.session_bus.add_signal_receiver(
						handler_function = call_back,
						signal_name = signal,
						dbus_interface = self.dbus_interface,
						path = self.dbus_path)

		MumblesPlugin.__init__(self, session_bus, options, verbose)

	def alert(self):
		pass
