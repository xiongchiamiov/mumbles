#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Options Handler
#
#------------------------------------------------------------------------

from MumblesGlobals import *
from OptionsHandler import *

class MumblesOptions(OptionsHandler):

	def __init__(self):
		OptionsHandler.__init__(self)
		self.options = {}
		self.options['mumbles'] = {
				# show/don't show debug messages 
				'verbosity' : 0,

				# run in deamon mode
				'daemon' : 0,

				# enable growl network handling
				'growl_network_enabled' : 0,
		}
		self.options['mumbles-notifications'] = {
				# placement and direction of notifications
				'notification_placement' : NOTIFY_PLACEMENT_RIGHT,
				'notification_direction' : NOTIFY_DIRECTION_DOWN,

				# how long to show the notifications (seconds)
				'notification_duration' : 5
		}

