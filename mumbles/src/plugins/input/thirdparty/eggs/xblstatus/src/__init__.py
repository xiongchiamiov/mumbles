#------------------------
# A Mumbles Plugin for XBL Status
#   Copyright (c) 2008 Chris Hollenbeck <chris.hollenbeck@gmail.com>
#   Licensed under the GPL
#------------------------

from MumblesInputPlugin import *

class XBLStatusMumbles(MumblesInputPlugin):

    plugin_name = "XBLStatusMumbles"
    
    dbus_interface = "com.hollec.xblstatus"
    
    dbus_path = "/com/hollec/xblstatus"
    
    icons = {'xblstatus' : 'xblstatus.png'}
    
    def __init__(self, session_bus, options = None, verbose = False):
    
        self.signal_config = { "notify" : self.Notify }
        
        MumblesInputPlugin.__init__(self, session_bus, options, verbose)
    
    
    def Notify(self, status, friend_info, gamerpic):
    
        self.set_icon(gamerpic)
        self.set_title(status)
        self.set_msg(friend_info)
        self.alert()
