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
		plugin_dir = ''

		dbus_interface = ''
		dbus_path = ''

		icons = {}
		signal_confg = {}

		def __init__(self, mumbles_notify, session_bus):

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

		def add_click_handler(self, handler):
			self.mumbles_notify.add_click_handler(self.plugin_name, handler)

		def get_icon(self, icon_name):
			if not self.icons[icon_name]:
				return None

			# try gettin icon from src path if not running installed version
			icon = os.path.join(PLUGIN_DIR, 'eggs', self.plugin_dir, 'src', 'themes', self.icons[icon_name])
			if os.path.isfile(icon):
				return icon

			# try getting icon from installed path
			icon = os.path.join(PLUGIN_DIR, 'icons', self.plugin_dir, self.icons[icon_name])
			if os.path.isfile(icon):
				return icon

			return None

