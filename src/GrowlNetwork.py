#!/usr/bin/env python

# Simple Growl Network Utilities 
# 	Steve Benz (steve.benz@gmail.com)
# 	dot_j (dot_j@mumbles-project.org)
# Original Idea, GrowlPacked by Rui Carmo (http://the.taoofmac.com)
# 		(C) 2006 Rui Carmo. Code under BSD License.
# Some of the request handler code is from technovelty.com
#    http://www.technovelty.org/code/python/socketserver.html

import SocketServer, time, select, sys, struct
from threading import Thread
import os
import dbus
import dbus.service
try:
	import hashlib
except ImportError:
	import md5

GROWL_UDP_PORT=9887
GROWL_PROTOCOL_VERSION=1
GROWL_TYPE_REGISTRATION=0
GROWL_TYPE_NOTIFICATION=1

GROWL_DBUS_NAME = 'info.growl.Growl'
GROWL_DBUS_OBJECT = '/info/growl/Growl'
GROWL_DBUS_INTERFACE = 'info.growl.Growl'

class GrowlDBus(dbus.service.Object):
	def __init__(self,bus_name):
		dbus.service.Object.__init__(self,bus_name,GROWL_DBUS_OBJECT)

	@dbus.service.signal(dbus_interface=GROWL_DBUS_INTERFACE, signature='ss')
	def Notify(self, title, message):
		pass

class GrowlPacket:
	"""Performs basic decoding of a Growl UDP Packet."""

	def __init__(self, data, password = None):
		"""Initializes and validates the packet"""
		self.valid = False
		self.data = data
		self.digest = self.data[-16:]
		try:
			checksum = hashlib.md5()
		except:
			checksum = md5.new()
		checksum.update(self.data[:-16])
		if password:
			checksum.update(password)
		if self.digest == checksum.digest():
			self.valid = True
	# end def

	def type(self):
		"""Returns the packet type"""
		if self.data[1] == '\x01':
			return 'NOTIFY'
		else:
			return 'REGISTER'
	# end def

	def info(self):
		"""Returns a subset of packet information"""
		if self.type() == 'NOTIFY':
			nlen = struct.unpack("!H",str(self.data[4:6]))[0]
			tlen = struct.unpack("!H",str(self.data[6:8]))[0]
			dlen = struct.unpack("!H",str(self.data[8:10]))[0]
			alen = struct.unpack("!H",str(self.data[10:12]))[0]
			return struct.unpack(("%ds%ds%ds%ds") % (nlen, tlen, dlen, alen), self.data[12:len(self.data)-16])
		else:
			length = struct.unpack("!H",str(self.data[2:4]))[0]
			return self.data[6:7+length]
	# end def
# end class

class GrowlNotificationPacket:
	"""Builds a Growl Network Notification packet.
	   Defaults to emulating the command-line growlnotify utility."""

	def __init__(self, application="growlnotify",
			notification="Command-Line Growl Notification", title="Title",
			description="Description", priority = 0, sticky = False, password = None ):

		self.application  = application.encode("utf-8")
		self.notification = notification.encode("utf-8")
		self.title        = title.encode("utf-8")
		self.description  = description.encode("utf-8")
		flags = (priority & 0x07) * 2

		if priority < 0:
			flags |= 0x08
		if sticky:
			flags = flags | 0x0001

		self.data = struct.pack( "!BBHHHHH",
			GROWL_PROTOCOL_VERSION,
			GROWL_TYPE_NOTIFICATION,
			flags,
			len(self.notification),
			len(self.title),
			len(self.description),
			len(self.application) )

		self.data += self.notification
		self.data += self.title
		self.data += self.description
		self.data += self.application

		try:
			self.checksum = hashlib.md5()
		except:
			self.checksum = md5.new()
		self.checksum.update(self.data)
		if password:
			self.checksum.update(password)
		self.data += self.checksum.digest()
	# end def

	def payload(self):
		"""Returns the packet payload."""
		return self.data
	# end def
# end class

class GrowlRegistrationPacket:
	"""Builds a Growl Network Registration packet.
	   Defaults to emulating the command-line growlnotify utility."""

	def __init__(self, application="growlnotify", password = None ):
		self.notifications = []
		self.defaults = [] # array of indexes into notifications
		self.application = application.encode("utf-8")
		self.password = password
	# end def


	def addNotification(self, notification="Command-Line Growl Notification", enabled=True):
		"""Adds a notification type and sets whether it is enabled on the GUI"""
		self.notifications.append(notification)
		if enabled:
			self.defaults.append(len(self.notifications)-1)
	# end def


	def payload(self):
		"""Returns the packet payload."""
		self.data = struct.pack( "!BBH",
			GROWL_PROTOCOL_VERSION,
			GROWL_TYPE_REGISTRATION,
			len(self.application) )

		self.data += struct.pack( "BB",
			len(self.notifications),
			len(self.defaults) )

		self.data += self.application

		for notification in self.notifications:
			encoded = notification.encode("utf-8")
			self.data += struct.pack("!H", len(encoded))
			self.data += encoded

		for default in self.defaults:
      			self.data += struct.pack("B", default)

		try:
			self.checksum = hashlib.md5()
		except:
			self.checksum = md5.new()
		self.checksum.update(self.data)
		if self.password:
			self.checksum.update(self.password)

		self.data += self.checksum.digest()
		return self.data
	# end def
# end class

# SimpleServer extends the UDPServer, using the threading mix in
# to create a new thread for every request.
class GrowlServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):

	# This means the main server will not do the equivalent of a
	# pthread_join() on the new threads.  With this set, Ctrl-C will
	# kill the server reliably.
	daemon_threads = True

	# By setting this we allow the server to re-bind to the address by
	# setting SO_REUSEADDR, meaning you don't have to wait for
	# timeouts when you kill the server and the sockets don't get
	# closed down correctly.
	allow_reuse_address = True

	active = False

	def __init__(self, server_address, RequestHandlerClass, password=None):
		self.password = password
		SocketServer.UDPServer.__init__(self, server_address, RequestHandlerClass)

		try:
			self.__bus = dbus.SessionBus()
		except:
			print "Error: DBus appears to not be running."
			return False

		dbus_object = self.__bus.get_object("org.freedesktop.DBus", "/org/freedesktop/DBus")
		dbus_iface = dbus.Interface(dbus_object, "org.freedesktop.DBus")
		name = dbus.service.BusName(GROWL_DBUS_NAME,bus=self.__bus)
		self.dbus = GrowlDBus(name)


	def update(self, active, password):
		self.active = active
		self.password = password


# The RequestHandler handles an incoming request.
class growlIncoming(SocketServer.DatagramRequestHandler):

	def __init__(self, request, client_address, server):
		SocketServer.DatagramRequestHandler.__init__(self, request, client_address, server)

	def handle(self):

		if self.server.active:
			p = GrowlPacket(self.rfile.read(), self.server.password)

		if p.valid:
			if p.type() == 'NOTIFY':
				notification,title,description,app = p.info()   

				mpath = os.path.dirname(__file__)
				self.server.dbus.Notify(title, description)

	def finish(self):
		pass
