#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Gaim Mumbles Plugin
#
#------------------------------------------------------------------------

from MumblesInputPlugin import *
import dbus
import re

class GaimMumbles(MumblesInputPlugin):

	plugin_name = "GaimMumbles"

	dbus_interface = "net.sf.gaim.GaimInterface"
	dbus_path = "/net/sf/gaim/GaimObject"

	dbus_name = "net.sf.gaim.GaimService"
	gaim_interface = None

	icons = {'gaim' : 'gaim.png', 'irc' : 'irc.png' }

	def __init__(self, session_bus, options = None, verbose = False):
		self.signal_config = {
			"ReceivedImMsg": self.ReceivedImMsg,
			"ReceivedChatMsg": self.ReceivedChatMsg
		}

		MumblesInputPlugin.__init__(self, session_bus, options, verbose)


	def ReceivedImMsg(self, account, name, message, conversation, flags):

		message = self.unescape(self.striphtml(message))
		icon = 0

		gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
		gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

		buddy = gaim_interface.GaimFindBuddy(account, name)
		if buddy != 0:
			name = gaim_interface.GaimBuddyGetAlias(buddy)

		name = self.unescape(name)

		self.set_title(name)
		self.set_msg(message)
		self.set_icon('gaim')
		self.alert()


	def ReceivedChatMsg(self, account, name, message, conversation, flags):

		message = self.unescape(self.striphtml(message))

		gaim_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
		gaim_interface = dbus.Interface(gaim_object, self.dbus_interface)

        	chatroom_name = gaim_interface.GaimConversationGetTitle(conversation)
        	chat_data = gaim_interface.GaimConversationGetChatData(conversation)

        	chat_nick = gaim_interface.GaimConvChatGetNick(chat_data)

        	if name != chat_nick:
                	name = chatroom_name+": "+name
			name = self.unescape(name)
			self.set_title(name)
			self.set_msg(message)
			self.set_icon('irc')
			self.alert()


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

