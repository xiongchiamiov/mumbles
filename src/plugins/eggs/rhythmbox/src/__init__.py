#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Rythmbox Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus

class RhythmboxMumbles(MumblesPlugin):

	plugin_name = "RhythmboxMumbles"

	dbus_interface = "org.gnome.Rhythmbox.Player"
	dbus_path = "/org/gnome/Rhythmbox/Player"

	dbus_name = "org.gnome.Rhythmbox"
	dbus_shell_interface = "org.gnome.Rhythmbox.Shell"
	dbus_shell_path = "/org/gnome/Rhythmbox/Shell"

	icons = {
		'rhythmbox' : 'rhythmbox.png'
	}

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"playingUriChanged": self.playingUriChanged
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)

	def playingUriChanged(self, uri):
		metadata = {}
		info = ["artist", "album", "title", "track-number"]

		rhythmbox_shell_object = self.session_bus.get_object(self.dbus_name, self.dbus_shell_path)
		shell = dbus.Interface(rhythmbox_shell_object, self.dbus_shell_interface)

		data = shell.getSongProperties(uri)
		for key in data:
			if key in info:
				metadata[key] = data[key]

		header = "%s - %s" %(metadata["artist"],metadata["album"])
		message = "%d: %s" %(metadata["track-number"],metadata["title"])
		icon = self.get_icon('rhythmbox')

		self.mumbles_notify.alert(self.plugin_name, header, message, icon)

