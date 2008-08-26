#------------------------------------------------------------------------
# A Mumbles Plugin for Evolution
#   Copyright (c) 2007 dot_j <dot_j[AT]mumbles-project[DOT]org>
#   Lisenced under the GPL
#------------------------------------------------------------------------

# We'll extend the MumblesPlugin class to create our Evolution plugin
from MumblesPlugin import *

class EvolutionMumbles(MumblesPlugin):

    # Give our plugin a name (using the same name we used in setup.py).
    plugin_name = "EvolutionMumbles"

    # Use the dbus interface we saw in dbus-notify
    dbus_interface = "org.gnome.evolution.mail.dbus.Signal"

    # Use the dbus path we saw in dbus-notify
    dbus_path = "/org/gnome/evolution/mail/newmail"

    # Configure our plugin icon
    icons = {'evolution' : 'evolution.png'}

    # setup the __init__ function where we define
    # the dbus signal(s), to which, we are connecting.
    # Note this function takes 2 parameters (mumbles_notify and
    # session_bus) that we will hand off to our
    # MumblesPlugin parent class
    def __init__(self, mumbles_notify, session_bus):

        # Here, we tell our plugin to connect the dbus signal
        # 'Newmail' to our plugin class's 'NewMail' function
        self.signal_config = {
            "Newmail": self.NewMail
        }

        # and hand off our mumbles_notify and session_bus objects to our parent
        MumblesPlugin.__init__(self, mumbles_notify, session_bus)

    # NewMail function
    # This will get called when a NewMail signal is received on the DBus from Evolution
    # Note the function takes 2 parameters (the two we saw in the dbus-monitor activity)
    def NewMail(self, mbox_path, folder_name, some_int=None):

        # Get our icon using the key we used above when configuring our icons dictionary
        icon = self.get_icon('evolution')

        # Define what we want to send in our notification:
        # Send a simple title
        title = 'Evolution: New Mail!'

        # Let's send our folder name as our notification message
        message = folder_name

        # If you want to try an advanced version of the plugin,
        # see if you can use the supplied mbox_path to get more information
        # about the message that just arrived! And be sure to let us know
        # about your efforts.

        # Finally, using our mumbles_notification object, send the notification
        self.mumbles_notify.alert(self.plugin_name, title, message, icon)
