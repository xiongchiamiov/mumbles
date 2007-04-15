#!/usr/bin/python
#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Generic Mumbles Example
#
# usage: mumbles-send.py title content
#------------------------------------------------------------------------

import sys
import getopt
import dbus

from MumblesGlobals import *

class Usage(Exception):
	def __init__(self, msg=None):
		self.msg = 'Usage: mumbles-send.py title content'

def main(argv=None):
	if argv is None:
		argv = sys.argv
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "h", ["help"])
			if opts in ("h", "help") or not len(args):
				raise Usage()

		except getopt.error, msg:
			raise Usage(msg)
	except Usage, err:
		print >>sys.stderr, err.msg
		return 2

	bus = dbus.SessionBus()
	obj = bus.get_object(MUMBLES_DBUS_NAME,MUMBLES_DBUS_OBJECT)
	sender = dbus.Interface(obj,MUMBLES_DBUS_NAME)

	content = ''
	if len(args) > 1:
		content = args[1]

	sender.Notify(args[0], content)

if __name__ == "__main__":
    sys.exit(main())
