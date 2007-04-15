#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles DBus Handler
#
#------------------------------------------------------------------------

import dbus
from MumblesGlobals import *

class MumblesDBus(dbus.service.Object):
	# for now, until the signal issue is worked out
	# pass a MumblesNotify object here to be used in
	# the notify Method
	def __init__(self,bus_name, mumbles_notify):
		dbus.service.Object.__init__(self,bus_name,MUMBLES_DBUS_OBJECT)
		self.mumbles_notify = mumbles_notify

	@dbus.service.method(MUMBLES_DBUS_NAME)
	def Notify(self, name, message):
		self.mumbles_notify.alert(name, message)

	'''
	# this seems like it should the the way to do this
	# using the generic plugin's callback, but
	# using a signal results in a NoReply error - why? 
	@dbus.service.signal(MUMBLES_DBUS_NAME)
	def Notify(self, name, message):
		pass
	'''
