
#------------------------------------------------------------------------
#   A core function plugin for mumbles
#   aegis
#   Licensed under the GPL
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
import gnomevfs
import os

class CoreFuncMumbles(MumblesPlugin):

	plugin_name = "CoreFuncMumbles"
	dbus_interface = "org.gnome.ScreenSaver"
	dbus_path = "/org/gnome/ScreenSaver"

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"SessionIdleChanged": self.SessionIdleChanged,
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)
	
	def clickHandler(self, widget, event, plugin_name):
		if event.button == 3:
			self.mumbles_notify.close(widget)
		self.mumbles_notify.resume()
		
 	def SessionIdleChanged(self, enabled):
 		if enabled:
	 		self.mumbles_notify.alert(self.plugin_name, "pausing", "session went idle", None)
 			self.mumbles_notify.pause()
 		else:
 			self.mumbles_notify.resume()
	 		self.mumbles_notify.alert(self.plugin_name, "resuming", "session no longer idle", None)
