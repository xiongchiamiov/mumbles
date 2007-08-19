#!/usr/bin/python
#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Example
#
# usage: mumbles-send.py title content
#
# python script to do the same as:
#
# dbus-send --type=signal --dest=org.mumblesproject.Mumbles /org/mumblesproject/Mumbles org.mumblesproject.Mumbles.Notify string:'subject' string:'content'
#
#------------------------------------------------------------------------

import sys
import getopt
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from socket import AF_INET, SOCK_DGRAM, socket
from getpass import getpass

from MumblesGlobals import *
from MumblesDBus import *
from GrowlNetwork import *

MUMBLES_SEND_ID = "mumbles-send"

class Usage(Exception):
	def __init__(self, msg=None):
		self.msg = 'Usage: mumbles-send.py [-l] [-g (ip)] [-p] title content'

def main(argv=None):

	send_local = False 
	send_network = False
	network_addr = None
	prompt_password = False

	if argv is None:
		argv = sys.argv
		try:
			try:
				opts, args = getopt.getopt(sys.argv[1:], "hlg:p", ["help", "local", "growl-network", "password"])
			except getopt.GetoptError:

				raise Usage()

			for o, a in opts:
				if o in ("-h", "--help"):
					raise Usage()
				elif o in ("-l", "--local"):
					send_local = True
				elif o in ("-g", "--growl-network"):
					if not a:
						raise Usage()
					send_network = True
					network_addr = a
				elif o in ("-p", "--password"):
					prompt_password = True
				else:
					raise Usage()
		except Usage, err:
			print >> sys.stderr, err.msg
			return 2

	if not send_network and not send_local:
		send_local = True


	content = ''
	if len(args) > 1:
		content = args[1]

	title = args[0]

	if send_local:
		dbus_loop = DBusGMainLoop()
		name = dbus.service.BusName (MUMBLES_DBUS_INTERFACE, bus=dbus.SessionBus(mainloop=dbus_loop))

		sender = MumblesDBus(name)
		sender.Notify(title, content)

	if send_network:
		passwd = None
		if prompt_password:
			passwd = getpass()

		addr = (network_addr, GROWL_UDP_PORT)
		s = socket(AF_INET,SOCK_DGRAM)

		p = GrowlRegistrationPacket(application=MUMBLES_SEND_ID, password=passwd)
		p.addNotification(notification=MUMBLES_SEND_ID, enabled=True)
		s.sendto(p.payload(),addr)

		p = GrowlNotificationPacket(application=MUMBLES_SEND_ID,
				notification=MUMBLES_SEND_ID,
				title=title,
				description=content,
				priority=1, sticky=False, password=passwd)
		s.sendto(p.payload(),addr)
		s.close()


if __name__ == "__main__":
    sys.exit(main())
