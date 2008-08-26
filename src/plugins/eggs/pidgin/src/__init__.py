#------------------------------------------------------------------------
# A Mumbles Plugin for Pidgin
#   Copyright (c) 2007 dot_j <dot_j[AT]mumbles-project[DOT]org>
#                 2008 reis.miliante[AT]gmail[DOT]com
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
    
    # Configure our plugin icon
    icons = {'pidgin' : 'pidgin.png'}

    # setup the __init__ function where we define
    # the dbus signal(s), to which, we are connecting.
    # Note this function takes 2 parameters (mumbles_notify and
    # session_bus) that we will hand off to our
    # MumblesPlugin parent class
    def __init__(self, mumbles_notify, session_bus):

        # Here, we tell our plugin to connect the dbus signal
        # 'Newmail' to our plugin class's 'NewMail' function
        self.signal_config = {
            "BuddyStatusChanged": self.BuddyStatusChanged,
            "BuddySignedOn": self.BuddySignedOn,
            "BuddySignedOff": self.BuddySignedOff,
            "ReceivedImMsg": self.ReceivedImMsg
        }

        # and hand off our mumbles_notify and session_bus objects to our parent
        MumblesPlugin.__init__(self, mumbles_notify, session_bus)

    def BuddyStatusChanged(self, buddy, old_status, status):
    	return # eh, I don't really want these shown

        # Get our icon using the key we used above when configuring our icons dictionary
        icon = self.get_icon('pidgin')

        pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
        pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)

        if buddy != 0:
              name = pidgin_interface.PurpleBuddyGetAlias(buddy)
#              stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
#              icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
              osts = pidgin_interface.PurpleStatusGetName(old_status)
              nsts = pidgin_interface.PurpleStatusGetName(status)
			
        # Define what we want to send in our notification:
        # Send a simple title
        title = name

        # Let's send our folder name as our notification message
        message = 'Change the status from '+osts+' to '+nsts

        # If you want to try an advanced version of the plugin,
        # see if you can use the supplied mbox_path to get more information
        # about the message that just arrived! And be sure to let us know
        # about your efforts.

        # Finally, using our mumbles_notification object, send the notification
        self.mumbles_notify.alert(self.plugin_name, title, message, icon)
        
    def BuddySignedOn(self, buddy):

        # Get our icon using the key we used above when configuring our icons dictionary
        icon = self.get_icon('pidgin')


        pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
        pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)

        if buddy != 0:
		stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
		if stp1: icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
		name = pidgin_interface.PurpleBuddyGetAlias(buddy)
			
        # Define what we want to send in our notification:
        # Send a simple title
        title = name

        # Let's send our folder name as our notification message
        message = 'Signed on'

        # If you want to try an advanced version of the plugin,
        # see if you can use the supplied mbox_path to get more information
        # about the message that just arrived! And be sure to let us know
        # about your efforts.

        # Finally, using our mumbles_notification object, send the notification
        self.mumbles_notify.alert(self.plugin_name, title, message, icon)
        
    def BuddySignedOff(self, buddy):

        # Get our icon using the key we used above when configuring our icons dictionary
        icon = self.get_icon('pidgin')

        pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
        pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)


        if buddy != 0:
		stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
		if stp1: icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
		name = pidgin_interface.PurpleBuddyGetAlias(buddy)
			
        # Define what we want to send in our notification:
        # Send a simple title
        title = name

        # Let's send our folder name as our notification message
        message = 'Signed off'

        # If you want to try an advanced version of the plugin,
        # see if you can use the supplied mbox_path to get more information
        # about the message that just arrived! And be sure to let us know
        # about your efforts.

        # Finally, using our mumbles_notification object, send the notification
        self.mumbles_notify.alert(self.plugin_name, title, message, icon)
        

    def ReceivedImMsg(self, account, name, message, conversation, flags):

        icon = self.get_icon('pidgin')

        pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
        pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)
        key = pidgin_interface.PurpleConversationHasFocus(conversation)

        if not key or True:

              buddy = pidgin_interface.PurpleFindBuddy(account, name)
              if buddy != 0:
			stp1 = pidgin_interface.PurpleBuddyGetIcon(buddy)
			if stp1: icon = pidgin_interface.PurpleBuddyIconGetFullPath(stp1)
			name = pidgin_interface.PurpleBuddyGetAlias(buddy)

              # Define what we want to send in our notification:
              # Send a simple title
              title = self.unescape(name)

              # Let's send our folder name as our notification message
              message = self.unescape(self.striphtml(message))

              # If you want to try an advanced version of the plugin,
              # see if you can use the supplied mbox_path to get more information
              # about the message that just arrived! And be sure to let us know
              # about your efforts.
		
              # Finally, using our mumbles_notification object, send the notification
              self.mumbles_notify.alert(self.plugin_name, title, message, icon)

# weird
#    def openConversation(self, conversation): # opens a conversation with a buddy
#		def launcher(widget, event, plugin_name):
#			pidgin_object = self.session_bus.get_object(self.dbus_name, self.dbus_path)
#			pidgin_interface = dbus.Interface(pidgin_object, self.dbus_interface)
#	 		if event.button == 3:
#	 			self.mumbles_notify.close(widget)
#	 		elif event.button == 2:
#	 			pass # something for middle click
#	 		else:
#	 			ctype = pidgin_interface.PurpleConversationGetType(conversation)
#	 			account = pidgin_interface.PurpleConversationGetAccount(conversation)
#	 			name = pidgin_interface.PurpleConversationGetName(conversation)
#	 			pidgin_interface.PurpleConversationNew(ctype, account, name)
#	 			pass # something for left click (any any other click)
#		return launcher

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

