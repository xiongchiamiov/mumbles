#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Gaim Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesPlugin import *
import dbus
import re

class GaimMumbles(MumblesPlugin):

	plugin_name = "GaimMumbles"
	dbus_interface = "net.sf.gaim.GaimInterface"
	dbus_path = "/net/sf/gaim/GaimObject"

	dbus_name = "net.sf.gaim.GaimService"
	gaim_interface = None

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"ReceivedImMsg": self.ReceivedImMsg,
			"ReceivedChatMsg": self.ReceivedChatMsg
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)


	def ReceivedImMsg(self, account, name, message, conversation, flags):

		message = self.striphtml(message)
		icon = 0

		if not self.gaim_interface:
			gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
			self.gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

		buddy = self.gaim_interface.GaimFindBuddy(account, name)
		if buddy != 0:
			name = self.gaim_interface.GaimBuddyGetAlias(buddy)

		icon = self.plugin_dir+"/gaim/gaim/themes/gaim.png"
		self.mumbles_notify.alert(self.plugin_name, name, message, icon)


	def ReceivedChatMsg(self, account, name, message, conversation, flags):

		message = self.striphtml(message)

		if not self.gaim_interface:
			gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
			self.gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

        	chatroom_name = self.gaim_interface.GaimConversationGetTitle(conversation)
        	chat_data = self.gaim_interface.GaimConversationGetChatData(conversation)

        	chat_nick = self.gaim_interface.GaimConvChatGetNick(chat_data)

        	if name != chat_nick:
                	name = chatroom_name+": "+name
			icon = self.plugin_dir+"/gaim/gaim/themes/irc.png"
			self.mumbles_notify.alert(self.plugin_name, name, message, icon)


	def striphtml(self, message):
		return re.compile('<[^>]+>').sub(' ',message)

