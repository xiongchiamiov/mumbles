#------------------------------------------------------------------------
# A Mumbles Plugin for Pidgin
#   Copyright (c) 2007 dot_j <dot_j[AT]mumbles-project[DOT]org>
#				 2008 reis.miliante[AT]gmail[DOT]com
#   Lisenced under the GPL
#------------------------------------------------------------------------

# We'll extend the MumblesPlugin class to create our Pidgin plugin
from MumblesPlugin import *
import dbus
import re

class PidginMumbles(MumblesPlugin):

	# Give our plugin a name (using the same name we used in setup.py).
	plugin_name = "PidginMumbles"

	# Use the dbus interface we saw in dbus-notify
	dbus_interface = "im.pidgin.purple.PurpleInterface"

	# Use the dbus path we saw in dbus-notify
	dbus_path = "/im/pidgin/purple/PurpleObject"

	dbus_name = "im.pidgin.purple.PurpleService"
	pidgin_interface = None
	
	# Configure our plugin icons
	icons = {'pidgin' : 'pidgin.png', 'irc' : 'irc.png'}

	def __init__(self, mumbles_notify, session_bus):

		# signal connection config
		# NOTE: comment out here to disable any of the features
		self.signal_config = {
			"BuddyStatusChanged": self.BuddyStatusChanged,
			"BuddySignedOn": self.BuddySignedOn,
			"BuddySignedOff": self.BuddySignedOff,
			"ReceivedImMsg": self.ReceivedImMsg,
			"ReceivedChatMsg": self.ReceivedChatMsg
		}

		# and hand off our mumbles_notify and session_bus objects to our parent
		MumblesPlugin.__init__(self, mumbles_notify, session_bus)


	def BuddyStatusChanged(self, buddy, old_status, status):

		if buddy:
			pidgin_interface = self.get_pidgin_interface()

			name = pidgin_interface.PurpleBuddyGetAlias(buddy)
			osts = pidgin_interface.PurpleStatusGetName(old_status)
			nsts = pidgin_interface.PurpleStatusGetName(status)
			
			title = name
			message = 'Change the status from '+osts+' to '+nsts
			icon = self.get_buddy_icon(buddy, pidgin_interface)
			self.mumbles_notify.alert(self.plugin_name, title, message, icon)

		
	def BuddySignedOn(self, buddy):

		if buddy:
			pidgin_interface = self.get_pidgin_interface()
			
			title = name
			message = 'Signed on'
			icon = self.get_buddy_icon(buddy, pidgin_interface)
			self.mumbles_notify.alert(self.plugin_name, title, message, icon)

		
	def BuddySignedOff(self, buddy):

		if buddy:
			pidgin_interface = self.get_pidgin_interface()
			
			title = name
			message = 'Signed off'
			icon = self.get_buddy_icon(buddy, pidgin_interface)
			self.mumbles_notify.alert(self.plugin_name, title, message, icon)
		

	def ReceivedImMsg(self, account, name, message, conversation, flags):

		pidgin_interface = self.get_pidgin_interface()
		key = pidgin_interface.PurpleConversationHasFocus(conversation)

		if not key or True:

			buddy = pidgin_interface.PurpleFindBuddy(account, name)
			name = pidgin_interface.PurpleBuddyGetAlias(buddy)

			title = self.unescape(name)
			message = self.unescape(self.striphtml(message))
			icon = self.get_buddy_icon(buddy, pidgin_interface)
			self.mumbles_notify.alert(self.plugin_name, title, message, icon)

	def ReceivedChatMsg(self, account, name, message, conversation, flags):

		pidgin_interface = self.get_pidgin_interface()
		key = pidgin_interface.PurpleConversationHasFocus(conversation)

		if not key or True:

			chatroom_name = pidgin_interface.PurpleConversationGetTitle(conversation)
			chat_data = pidgin_interface.PurpleConversationGetChatData(conversation)

			chat_nick = pidgin_interface.PurpleConvChatGetNick(chat_data)

			if name != chat_nick:
				title = self.unescape(chatroom_name+": "+name)
				message = self.unescape(self.striphtml(message))
				icon = self.get_buddy_icon(buddy, pidgin_interface)
				self.mumbles_notify.alert(self.plugin_name, title, message, icon)


	'''
 	# weird...
	def openConversation(self, conversation): # opens a conversation with a buddy
		def launcher(widget, event, plugin_name):
			pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
			pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)
			 if event.button == 3:
				 self.mumbles_notify.close(widget)
			 elif event.button == 2:
				 pass # something for middle click
			 else:
				 ctype = pidgin_interface.PurpleConversationGetType(conversation)
				 account = pidgin_interface.PurpleConversationGetAccount(conversation)
				 name = pidgin_interface.PurpleConversationGetName(conversation)
				 pidgin_interface.PurpleConversationNew(ctype, account, name)
				 pass # something for left click (any any other click)
		return launcher
	'''

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

	def get_pidgin_interface(self):
		pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
		return dbus.Interface(pidgin_object, self.dbus_interface)

	def get_buddy_icon(self, buddy, pidgin_interface):

		icon = None
		if buddy:
			stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
			if stp1:
				icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
		if not icon:
			icon = self.get_icon('pidgin')

		return icon


