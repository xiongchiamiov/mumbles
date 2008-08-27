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
		if buddy != 0:
			pidgin_interface = self.get_pidgin_interface()

			osts = pidgin_interface.PurpleStatusGetName(old_status)
			nsts = pidgin_interface.PurpleStatusGetName(status)

			if osts != nsts:
				name = pidgin_interface.PurpleBuddyGetAlias(buddy)
				message = 'changed status from '+osts+' to '+nsts
				icon = self.get_buddy_icon(pidgin_interface, buddy)

				self.pidgin_notify(name, message, icon)

		
	def BuddySignedOn(self, buddy):
		if buddy != 0:
			pidgin_interface = self.get_pidgin_interface()

			name = pidgin_interface.PurpleBuddyGetAlias(buddy)
			message = 'signed on'
			icon = self.get_buddy_icon(pidgin_interface, buddy)

			self.pidgin_notify(name, message, icon)

		
	def BuddySignedOff(self, buddy):
		if buddy != 0:
			pidgin_interface = self.get_pidgin_interface()
			
			name = pidgin_interface.PurpleBuddyGetAlias(buddy)
			message = 'signed off'
			icon = self.get_buddy_icon(pidgin_interface, buddy)

			self.pidgin_notify(name, message, icon)
		

	def ReceivedImMsg(self, account, name, message, conversation, flags):
		pidgin_interface = self.get_pidgin_interface()
	
		#TODO figure out if the pidgin window is in focus (not just the conversation)
		#has_focus = pidgin_interface.PurpleConversationHasFocus(conversation)
		has_focus = 1

		if has_focus != 0:
			buddy = pidgin_interface.PurpleFindBuddy(account, name)

			if buddy != 0:
				name = pidgin_interface.PurpleBuddyGetAlias(buddy)
				icon = self.get_buddy_icon(pidgin_interface, buddy)

				self.pidgin_notify(name, message, icon)

	def ReceivedChatMsg(self, account, name, message, conversation, flags):

		pidgin_interface = self.get_pidgin_interface()

		#TODO figure out if the pidgin window is in focus (not just the conversation)
		#has_focus = pidgin_interface.PurpleConversationHasFocus(conversation)
		has_focus = 1

		if has_focus != 0:
			chatroom_name = pidgin_interface.PurpleConversationGetTitle(conversation)
			chat_data = pidgin_interface.PurpleConversationGetChatData(conversation)

			chat_nick = pidgin_interface.PurpleConvChatGetNick(chat_data)

			if name != chat_nick:
				title = chatroom_name+": "+name
				icon = self.get_buddy_icon(pidgin_interface)
				self.pidgin_notify(name, message, icon)



	def clean(self, s):
		s = re.compile('<[^>]+>').sub(' ',s)
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&apos;", "'")
		s = s.replace("&quot;", '"')
		# this has to be last:
		s = s.replace("&amp;", "&")
		return s


	def pidgin_notify(self, title, message, icon):
		title = self.clean(title)
		message = self.clean(message)
		self.mumbles_notify.alert(self.plugin_name, title, message, icon)


	def get_pidgin_interface(self):
		pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
		return dbus.Interface(pidgin_object, self.dbus_interface)


	def get_buddy_icon(self, pidgin_interface, buddy = 0):
		icon = 0
		if buddy != 0:
			stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
			if stp1 != 0:
				icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
		if icon == 0:
			icon = self.get_icon('pidgin')

		return icon


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




