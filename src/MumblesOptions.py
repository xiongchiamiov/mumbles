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
		self.options['mumbles'] = {
			# placement and direction of notifications
			'notification_placement' : NOTIFY_PLACEMENT_RIGHT,
			'notification_direction' : NOTIFY_DIRECTION_DOWN,

			# how long to show the notifications (seconds)
			'notification_duration' : 5
		}

