#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Options Handler Parent Class
#
#------------------------------------------------------------------------

import os
import ConfigParser
from MumblesGlobals import *

class OptionsHandler(object):

	def __init__(self):
		self.filename = os.path.join(CONFIG_DIR, CONFIG_FILE)
		self.options = {}
		self.__config_parser = ConfigParser.ConfigParser()

	def save(self):
		for section in self.options:
			if not self.__config_parser.has_section(section):
				self.__config_parser.add_section(section)
			for option in self.options[section]:
				self.__config_parser.set(section, option, self.options[section][option])
		try:
			f = open(self.filename, 'w')
			self.__config_parser.write(f)
			f.close()
		except:
			print "Error: unable to write config file"

	def load(self):

		if os.path.isfile(self.filename):
			self.config_file = self.__config_parser.read(self.filename)

			for section in self.options:
				for option in self.__config_parser.options(section):
					self.options[section][option] = self.__config_parser.get(section, option)

	def get_option(self, section, option):
		return self.options[section][option]

	def set_option(self, section, option, value):
		self.options[section][option] = value

	def add_options(self, options):
		opts = options.options
		for o in opts:
			if o in self.options:
				self.options[o] = [self.options[o], opts[0]]
			else:
				self.options[o] = opts[o]

	def create_file(self, options):
		try:
			if not os.path.isdir(CONFIG_DIR):
				os.mkdir(CONFIG_DIR)
			if not os.path.isfile(CONFIG_FILE):
				self.options = options
				self.save()
		except:
			print "Error: unable to create config file"
