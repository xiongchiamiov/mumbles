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

	icons = {'gaim' : 'gaim.png', 'irc' : 'irc.png' }

	def __init__(self, mumbles_notify, session_bus):
		self.signal_config = {
			"ReceivedImMsg": self.ReceivedImMsg,
			"ReceivedChatMsg": self.ReceivedChatMsg
		}

		MumblesPlugin.__init__(self, mumbles_notify, session_bus)


	def ReceivedImMsg(self, account, name, message, conversation, flags):

		message = self.unescape(self.striphtml(message))
		icon = 0

		if not self.gaim_interface:
			gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
			self.gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

		buddy = self.gaim_interface.GaimFindBuddy(account, name)
		if buddy != 0:
			name = self.gaim_interface.GaimBuddyGetAlias(buddy)

		name = self.unescape(name)

		icon = self.get_icon('gaim')
		self.mumbles_notify.alert(self.plugin_name, name, message, icon)


	def ReceivedChatMsg(self, account, name, message, conversation, flags):

		message = self.unescape(self.striphtml(message))

		if not self.gaim_interface:
			gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
			self.gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

        	chatroom_name = self.gaim_interface.GaimConversationGetTitle(conversation)
        	chat_data = self.gaim_interface.GaimConversationGetChatData(conversation)

        	chat_nick = self.gaim_interface.GaimConvChatGetNick(chat_data)

        	if name != chat_nick:
                	name = chatroom_name+": "+name
			name = self.unescape(name)
			icon = self.get_icon('irc')
			self.mumbles_notify.alert(self.plugin_name, name, message, icon)


	def striphtml(self, message):
		return re.compile('<[^>]+>').sub(' ',message)

	def unescape(self, s):
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&apos;", "'")
		s = s.replace("&quot;", '"')
		# this has to be last:
		s = s.replace("&amp;", "&")
		return s

