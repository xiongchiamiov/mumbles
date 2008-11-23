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
		self.options[CONFIG_M] = {
				# show/don't show debug messages 
				'verbose' : 0,

				# run in deamon mode
				'daemon' : 0,

				# enable growl network handling
				'growl_network_enabled' : 0,

				# growl network handling password
				'growl_network_enabled' : ''
		}
		self.options[CONFIG_MN] = {
				# placement and direction of notifications
				'notification_placement' : CONFIG_NOTIFY_PLACEMENT_RIGHT,
				'notification_direction' : CONFIG_NOTIFY_DIRECTION_DOWN,
				
				# effects
				'horizontal_sliding_enabled': 0,
				'vertical_sliding_enabled': 0,
				
				'always_mask_enabled': 0,

				# how long to show the notifications (seconds)
				'notification_duration' : 5,

				# theme directory
				'theme' : 'default'
		}

