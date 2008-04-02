#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Shell
# Plugins extend this class to define their own call backs
#
#------------------------------------------------------------------------

from MumblesPlugin import *
from MumblesAlert import *

class MumblesInputPlugin(MumblesPlugin):

	dbus_interface = ''
	dbus_path = ''

	icons = {}
	signal_config = {}

	alert_object = None


	def __init__(self, session_bus, options = None, verbose = False):

		self.session_bus = session_bus
		self.alert_object = MumblesAlert(self.plugin_name)

		for signal, call_back in self.signal_config.items():
			self.session_bus.add_signal_receiver(
				handler_function = call_back,
				signal_name = signal,
				dbus_interface = self.dbus_interface,
				path = self.dbus_path)

		MumblesPlugin.__init__(self, session_bus, options, verbose)


	def set_title(self, title):
		self.alert_object.set_title(title)

	def set_msg(self, msg):
		self.alert_object.set_msg(msg)

	def set_icon(self, icon_name):
		icon = self._get_icon_by_name(icon_name)
		self.alert_object.set_icon(icon)

	def alert(self):
		self._input_alert()

	def add_click_handler(self, handler):
		self._input_add_click_handler(handler)
		pass


	def _get_icon_by_name(self, icon_name):
		if not self.icons[icon_name]:
			return None

		icon = os.path.join(PLUGIN_DIR_INPUT_USER, 'icons', self.icons[icon_name])
		if os.path.isfile(icon):
			return icon

		icon = os.path.join(PLUGIN_DIR_INPUT_CORE, 'icons', self.icons[icon_name])
		if os.path.isfile(icon):
			return icon

		icon = os.path.join(PLUGIN_DIR_INPUT_THIRDPARTY, 'icons', self.icons[icon_name])
		if os.path.isfile(icon):
			return icon

		return None
