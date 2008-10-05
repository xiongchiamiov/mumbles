#------------------------------------------------------------------------
# A Mumbles Plugin for Telepathy
#   Copyright (c) 2007 dot_j <dot_j[AT]mumbles-project[DOT]org>
#				 2008 reis.miliante[AT]gmail[DOT]com
#   Lisenced under the GPL
#------------------------------------------------------------------------

# We'll extend the MumblesPlugin class to create our Telepathy plugin
from MumblesPlugin import *
import dbus
import re

class TelepathyMumbles(MumblesPlugin):

	# Give our plugin a name (using the same name we used in setup.py).
	plugin_name = "TelepathynMumbles"

	dbus_interface = "org.freedesktop.Telepathy.Channel.Type.Text"
	dbus_path = None
	
	def __init__(self, mumbles_notify, session_bus):

		self.signal_config = {
			"Received": self.ReceivedMsg,
		}

		# send interface_keywork and path_keyword through
		# to our add_signal_receiver
		extra_info = {
			'interface_keyword': 'dbus_interface',
			'path_keyword': 'dbus_path'
		}

		# and hand off our mumbles_notify and session_bus objects to our parent
		MumblesPlugin.__init__(self, mumbles_notify, session_bus, **extra_info)

	def ReceivedMsg(self, id, timestamp, sender, type, flag, text, dbus_interface, dbus_path):
		'''
		ReceivedMsg callback
		'''
		title = self.get_contact_alias(dbus_path, sender)
		avatar = self.get_contact_avatar(dbus_path, sender)
		self.telepathy_notify(title, text, avatar)

	def telepathy_notify(self, title, message, icon = None):
		'''
		Send the mumbles notification
		'''
		self.mumbles_notify.alert(self.plugin_name, title, message, icon)

	def get_contact_alias(self, path, contact_handle):
		'''
		Get the contact alias
		'''
		telepathy_object = self.get_object(path)
		i = dbus.Interface(telepathy_object, 'org.freedesktop.Telepathy.Connection.Interface.Aliasing')
		return i.RequestAliases([contact_handle])[0]

	def get_contact_avatar(self, path, contact_handle):
		'''
		Get the contact avatar
		'''
		telepathy_object = self.get_object(path)
		i = dbus.Interface(telepathy_object, 'org.freedesktop.Telepathy.Connection.Interface.Avatars')
		image, mime = i.RequestAvatar(contact_handle)
		if image:
			return ''.join(chr(i) for i in image)
		else:
			return None

	def get_object(self, path):
		'''
		Get the bus object for the sender path
		'''
		interface = path.replace("/", ".")
		interface = interface[1:]
		interface = re.compile('\\.\\w+$').sub('',interface)

		path = re.compile('\\/\\w+$').sub('',path)

		telepathy_object = self.session_bus.get_object(interface, path)
		return telepathy_object
