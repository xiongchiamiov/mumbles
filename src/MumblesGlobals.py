#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Constants
#
#------------------------------------------------------------------------

import os

MUMBLES_DBUS_NAME = 'org.mumblesproject.Mumbles'
MUMBLES_DBUS_OBJECT = '/org/mumblesproject/Mumbles'
MUMBLES_DBUS_INTERFACE = 'org.mumblesproject.Mumbles'

DBUS_NAME = "org.freedesktop.DBus"
DBUS_OBJECT = "/org/freedesktop/DBus"

ENTRY_POINT = 'mumbles.plugins'

SRC_DIR = os.path.dirname(__file__)
PLUGIN_DIR = os.path.join(SRC_DIR, 'plugins')
THEMES_DIR = os.path.join(SRC_DIR, 'themes')
UI_DIR = os.path.join(SRC_DIR, 'ui')

PANEL_GLADE_FILE = os.path.join(UI_DIR, 'panel.glade')
PREFERENCES_GLADE_FILE = os.path.join(UI_DIR, 'preferences.glade')

CONFIG_DIR = os.path.join(os.environ["HOME"], '.mumbles')
CONFIG_FILE = "mumbles.conf"

NOTIFY_DIRECTION_DOWN = 0
NOTIFY_DIRECTION_UP = 1
NOTIFY_PLACEMENT_LEFT = 0
NOTIFY_PLACEMENT_RIGHT = 1
