#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Constants
#
#------------------------------------------------------------------------

import os

# If MUMBLES_PATH is not set, that is, Mumbles is running locally,
# use paths relative to the current running directory instead of /usr ones.
data_path = os.getenv("MUMBLES_PATH")
if not data_path:
	data_path = os.path.dirname(os.path.abspath(__file__))

PLUGIN_DIR = os.path.join(data_path, 'plugins')
PLUGIN_DIR_USER = os.path.expanduser('~/.mumbles/plugins/')
THEMES_DIR = os.path.join(data_path, 'themes')
UI_DIR = os.path.join(data_path, 'ui')

MUMBLES_DBUS_NAME = 'org.mumblesproject.Mumbles'
MUMBLES_DBUS_OBJECT = '/org/mumblesproject/Mumbles'
MUMBLES_DBUS_INTERFACE = 'org.mumblesproject.Mumbles'

DBUS_NAME = "org.freedesktop.DBus"
DBUS_OBJECT = "/org/freedesktop/DBus"

ENTRY_POINT = 'mumbles.plugins'

PANEL_GLADE_FILE = os.path.join(UI_DIR, 'panel.glade')
PREFERENCES_GLADE_FILE = os.path.join(UI_DIR, 'preferences.glade')

CONFIG_FILE = os.path.expanduser("~/.mumbles/mumbles.conf")
CONFIG_M = 'mumbles'
CONFIG_MN = 'mumbles-notifications'
CONFIG_MT = 'mumbles-theme'
CONFIG_NOTIFY_DIRECTION_DOWN = 0
CONFIG_NOTIFY_DIRECTION_UP = 1
CONFIG_NOTIFY_PLACEMENT_LEFT = 0
CONFIG_NOTIFY_PLACEMENT_RIGHT = 1
