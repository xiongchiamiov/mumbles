#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Alert Object
#------------------------------------------------------------------------

from MumblesGlobals import *

class MumblesAlert(object):

	name = ''
	title = ''
	msg = ''
	icon = None

	def __init__(self, name):
		self.set_name(name)

	def get_name(self):
		return self.name

	def set_name(self, name):
		self.name = name

	def get_title(self):
		return self.title

	def set_title(self, title):
		self.title = title

	def get_msg(self):
		return self.msg

	def set_msg(self, msg):
		self.msg = msg

	def get_icon(self):
		return self.icon

	def set_icon(self, icon):
		self.icon = icon

	def to_string(self):
		return self.title+": "+self.msg
