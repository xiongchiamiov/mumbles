#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Gaim Mumbles Plugin
#
#------------------------------------------------------------------------

import MumblesPlugin
import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
        import dbus.glib
import re


class GaimMumbles(MumblesPlugin.MumblesPlugin):

	__name__ = 'GaimMumbles'
	__dbus_name__ = "net.sf.gaim.GaimService"

	dbus_interface = "net.sf.gaim.GaimInterface"
	dbus_object = "/net/sf/gaim/GaimObject"


	def ReceivedImMsg(self, account, name, message, conversation, flags):
		message = self.striphtml(message)
		icon = 0

		buddy = self.interface.GaimFindBuddy(account, name)
		if buddy != 0:
			name = self.interface.GaimBuddyGetAlias(buddy)

		icon = self.plugin_dir+"/gaim/gaim/themes/gaim.png"
		self.mumbles_notify.alert(name, message, icon)


	def ReceivedChatMsg(self, account, name, message, conversation, flags):
		message = self.striphtml(message)
        	chatroom_name = self.interface.GaimConversationGetTitle(conversation)
        	chat_data = self.interface.GaimConversationGetChatData(conversation)

        	chat_nick = self.interface.GaimConvChatGetNick(chat_data)

        	if name != chat_nick:
                	name = chatroom_name+": "+name
			icon = self.plugin_dir+"/gaim/gaim/themes/irc.png"
			self.mumbles_notify.alert(name, message, icon)


	def connect_signals(self):
		self.interface.connect_to_signal("ReceivedImMsg", self.ReceivedImMsg)
		self.interface.connect_to_signal("ReceivedChatMsg", self.ReceivedChatMsg)

	def create(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify

		try:
			gaim_object = session_bus.get_object(self.get_dbus_name(), self.dbus_object)
			self.interface = dbus.Interface(gaim_object, self.dbus_interface)

			self.connect_signals()
			return True
		except:
			return False

	def striphtml(self, message):
		return re.compile('<[^>]+>').sub(' ',message)

