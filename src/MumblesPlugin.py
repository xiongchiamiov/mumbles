#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Shell
# Plugins extend this class to provide a few general hooks
#
#------------------------------------------------------------------------

from MumblesGlobals import *

class MumblesPlugin(object):

		def __init__(self):
			self.plugin_dir = PLUGIN_DIR

		def get_dbus_name(self):
			return self.__dbus_name__

		def get_name(self):
			return self.__name__
