#------------------------
# A Mumbles Plugin for XBL Status
#   Copyright (c) 2008 Chris Hollenbeck <chris.hollenbeck@gmail.com>
#   Licensed under the GPL
#------------------------

from MumblesPlugin import *

class XBLStatusMumbles(MumblesPlugin):

    plugin_name = "XBLStatusMumbles"
    
    dbus_interface = "com.hollec.xblstatus"
    
    dbus_path = "/com/hollec/xblstatus"
    
    icons = {'xblstatus' : 'xblstatus.png'}
    
    def __init__(self, mumbles_notify, session_bus):
    
        self.signal_config = { "notify" : self.Notify }
        
        MumblesPlugin.__init__(self, mumbles_notify, session_bus)
    
    
    def Notify(self, status, friend_info, gamerpic):
    
        icon = gamerpic
        
        title = status
        
        message = friend_info
        
        self.mumbles_notify.alert(self.plugin_name, title, message, icon)
