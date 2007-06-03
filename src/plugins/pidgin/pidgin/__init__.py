#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Pidgin Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
        import dbus.glib
import re


class PidginMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'PidginMumbles'
	__dbus_name__ = "im.pidgin.purple.PurpleService"

	dbus_interface = "im.pidgin.purple.PurpleInterface"
	dbus_object = "/im/pidgin/purple/PurpleObject"


	def ReceivedImMsg(self, account, name, message, conversation, flags):

		message = self.striphtml(message)
		icon = 0

		buddy = self.interface.PurpleFindBuddy(account, name)
		if buddy != 0:
			name = self.interface.PurpleBuddyGetAlias(buddy)

		icon = self.plugin_dir+"/pidgin/pidgin/themes/pidgin.png"
		self.mumbles_notify.alert(name, message, icon)


	def ReceivedChatMsg(self, account, name, message, conversation, flags):
		message = self.striphtml(message)
        	chatroom_name = self.interface.PurpleConversationGetTitle(conversation)
        	chat_data = self.interface.PurpleConversationGetChatData(conversation)

        	chat_nick = self.interface.PurpleConvChatGetNick(chat_data)

        	if name != chat_nick:
                	name = chatroom_name+": "+name
			icon = self.plugin_dir+"/pidgin/pidgin/themes/irc.png"
			self.mumbles_notify.alert(name, message, icon)


	def connect_signals(self):
		self.interface.connect_to_signal("ReceivedImMsg", self.ReceivedImMsg)
		self.interface.connect_to_signal("ReceivedChatMsg", self.ReceivedChatMsg)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		try:
			pidgin_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(pidgin_object, self.dbus_interface)

			self.connect_signals()
			return True
		except:
			return False

	def striphtml(self, message):
		return re.compile('<[^>]+>').sub(' ',message)

