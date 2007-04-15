#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Rythmbox Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
	import dbus.glib
from cgi import escape


class RhythmboxMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'RhythmboxMumbles'
	__dbus_name__ = "org.gnome.Rhythmbox"

	dbus_player_interface = "org.gnome.Rhythmbox.Player"
	dbus_player_object = "/org/gnome/Rhythmbox/Player"
	dbus_shell_interface = "org.gnome.Rhythmbox.Shell"
	dbus_shell_object = "/org/gnome/Rhythmbox/Shell"

	player = None
	shell = None

	def playingUriChanged(self, uri):
		metadata = {}
		info = ["artist", "album", "title", "track-number"]

		data = self.shell.getSongProperties(uri)
		for key in data:
			if key in info:
				metadata[key] = data[key]

		header = escape("%s - %s" %(metadata["artist"],metadata["album"]))
		message = escape("%d: %s" %(metadata["track-number"],metadata["title"]))

		icon = self.plugin_dir+"/rhythmbox/rhythmbox/themes/rhythmbox.xpm"
		self.mumbles_notify.alert(header, message, icon)

	def connect_signals(self):
		self.player.connect_to_signal("playingUriChanged", self.playingUriChanged)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify
		try:
			rhythmbox_player_object = session_bus.get_object(self.get_dbus_name(), self.dbus_player_object)
			self.player = dbus.Interface(rhythmbox_player_object, self.dbus_player_interface)

			rhythmbox_shell_object = session_bus.get_object(self.get_dbus_name(), self.dbus_shell_object)
			self.shell = dbus.Interface(rhythmbox_shell_object, self.dbus_shell_interface)

			self.connect_signals()
			return True
		except:
			return False
