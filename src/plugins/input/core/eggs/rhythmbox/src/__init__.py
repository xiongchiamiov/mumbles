#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Rythmbox Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus

class RhythmboxMumbles(MumblesInputPlugin):

	plugin_name = "RhythmboxMumbles"

	dbus_interface = "org.gnome.Rhythmbox.Player"
	dbus_path = "/org/gnome/Rhythmbox/Player"

	dbus_name = "org.gnome.Rhythmbox"
	dbus_shell_interface = "org.gnome.Rhythmbox.Shell"
	dbus_shell_path = "/org/gnome/Rhythmbox/Shell"

	icons = {
		'rhythmbox' : 'rhythmbox.png'
	}

	def __init__(self, session_bus, options=None, verbose=False):
		self.signal_config = {
			"playingUriChanged": self.playingUriChanged
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)

	def playingUriChanged(self, uri):
		metadata = {}
		info = ["artist", "album", "title", "track-number"]

		rhythmbox_shell_object = self.session_bus.get_object(self.dbus_name, self.dbus_shell_path, False)
		shell = dbus.Interface(rhythmbox_shell_object, self.dbus_shell_interface)
		if uri:
			data = shell.getSongProperties(uri)
			for key in data:
				if key in info:
					metadata[key] = data[key]

			header = metadata["title"]
			message = "%s - %s\nTrack: %d" %(metadata["artist"],metadata["album"],metadata["track-number"])
			self.set_title(header)
			self.set_msg(message)
			self.set_icon('rhythmbox')
			self.alert()

