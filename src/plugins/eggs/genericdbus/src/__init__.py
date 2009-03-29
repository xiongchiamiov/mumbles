
#------------------------------------------------------------------------
#   A (TOTALLY AWESOME) Generic DBUS Plugin for mumbles - Works for any mostly "dumb" notification over dbus :D
#   aegis
#   Licensed under the GPL
#------------------------------------------------------------------------

from MumblesPlugin import *
from MumblesGlobals import *

import sys, os, gnomevfs, re, traceback
from ConfigParser import ConfigParser
import gtk
import shutil

class GenericDBUSMumbles(MumblesPlugin):

	plugin_name = "GenericDBUSMumbles"
	config_dir = os.path.join(os.path.expanduser('~'), '.mumbles', 'generic')
	dbus_watches = {}
	replace = {}

	def __init__(self, mumbles_notify, session_bus):
		self.mumbles_notify = mumbles_notify
		self.session_bus = session_bus

		self.initConfig()
		
		self.parseConfig()
		
		for watch in self.dbus_watches.values():
			self.session_bus.add_signal_receiver(
				handler_function = self.notify,
				signal_name = watch['signal'],
				dbus_interface = watch['interface'],
				path = watch['path'],)

	def initConfig(self):
		if not os.path.isdir(self.config_dir):
			examples = os.path.join(PLUGIN_DIR, 'eggs', 'genericdbus', 'examples')
			shutil.copytree(examples, self.config_dir)
	
	def parseConfig(self):
		# do magic to figure out where to parse from etc
		config_files = []
		tmp_list = os.listdir(self.config_dir)
		for tmp_conf in tmp_list:
			config_files.append( os.path.join(self.config_dir, tmp_conf) )
		# parse the config file(s)
		parser = ConfigParser()
		parser.read(config_files)
		i = 0
		for section in parser.sections():
			i += 1
			watch = {'name':section, 'enabled':True, 'interface':None, 'path':None, 'signal':None, 'icon':'unknown.png', 'linkdetect':False, 'launch':None, 'launchalt':None, 'launchmime':False, 'launchclose':False, 'launchreplace':False, 'replaceinplace':True} # set defaults
			watch.update(parser.defaults()) # update from config file defaults
			for item, value in parser.items(section):
				if item in ['interface', 'path', 'signal', 'icon', 'launch', 'launchalt']: # string config vars
					watch[item] = value
				elif item in ['enabled', 'unescape', 'striphtml', 'alwaysreplace', 'launchmime', 'launchclose', 'launchreplace', 'replaceinplace', 'linkdetect']: # boolean config vars
					watch[item] = (value.lower() == 'true')
			if not watch['enabled']: continue
			if None in (watch['interface'], watch['path'], watch['signal']):
				self.Error('Invalid config section', 'Invalid section in dbus.conf.\nSection was "%s"' % section)
			else:
				watch['id'] = i
				self.dbus_watches[i] = watch
				
	def detectURIs(self, args):
		uris = []
		if type(args) == list or type(args) == tuple:
			for arg in args:
				for uri in arg.split(' '):
					if '://' in uri:
						if not uri in uris: uris.append(uri)
		else:
			for uri in args.split(' '):
				if '://' in uri:
					if not uri in uris: uris.append(uri)
		for uri in uris:
			self.mumbles_notify.alert(self.plugin_name, 'Auto URI', uri, None, self.launchURIHandler(uri))
	
	def launchURIHandler(self, uri):
		def launcher(widget, event, plugin_name):
			self.open_uri(uri)
			return False
		return launcher
	
	def clickHandler(self, watch, args, launch=None, launchalt=None, mime=False): # defines and returns a function from this scope..
		if not launch: launch = watch['launch']
		if not launchalt: launchalt = watch['launchalt']
		launchreplace, launchclose = watch['launchreplace'], watch['launchclose']
		linkdetect = watch['linkdetect']
		def launcher(widget, event, plugin_name): # the function inherits the vars passed to the previous function but can have different vars passed :D - coolest hack ever
	 		if event.button == 3:
	 			self.mumbles_notify.close(widget)
	 		elif event.button == 2:
	 			if launchreplace:
	 				self.mark_replace(watch, widget)
		 		elif launchclose:
		 			self.mumbles_notify.close(widget)
	 			if launchalt:
	 				self.launch_exec(launchalt)
	 			elif linkdetect:
	 				self.detectURIs(args)
	 			elif mime:
	 				self.open_uri(launch)
	 		else:
	 			if launchreplace:
		 			self.mark_replace(watch, widget)
		 		if launchclose:
		 			self.mumbles_notify.close(widget)
		 		if linkdetect:
	 				self.detectURIs(args)
	 			elif mime:
	 				self.open_uri(launch)
	 			elif launch:
	 				self.launch_exec(launch)
		return launcher

	def notify(self, title, *args):
		cflocals = sys._getframe(2).f_locals # check two execution frames ago to see which dbus signal this came from
		interface, path, signal = cflocals['dbus_interface'], cflocals['path'], cflocals['signal_name']
		icon = None
		for watch in self.dbus_watches.values(): # iterate through all of the watches
			if (interface, path, signal) == (watch['interface'], watch['path'], watch['signal']): # find the watch matching the signal
				icon = self.get_icon(watch['icon']) # get the icon, if any
				message = '\n'.join(args)
				if watch['striphtml']: message = self.striphtml(message)
				if watch['unescape']: message = self.unescape(message)
				click_handler = self.get_click_handler(watch, args)
				widget = self.do_replace(watch)
				if widget and watch['replaceinplace']:
					widget = self.mumbles_notify.replace_alert(widget, self.plugin_name, title, message, icon, click_handler)
				else:
					widget = self.mumbles_notify.alert(self.plugin_name, title, message, icon, click_handler, widget)
				if watch['alwaysreplace']: self.mark_replace(watch, widget)
				# you can do more than one listen for the same signal in the config if you really want to...
	
	def do_replace(self, watch):
		if watch['id'] in self.replace:
			widget = self.replace[watch['id']]
			del self.replace[watch['id']]
			return widget
	
	def mark_replace(self, watch, widget):
		self.replace[watch['id']] = widget
	
	def get_click_handler(self, watch, args):
		if watch['launchmime']:
			if watch['launchalt']:
				return self.clickHandler(watch, args, args[-1], mime=True)
			else:
				return self.clickHandler(watch, args, args[-1], mime=True)
		elif watch['launch'] or watch['launchalt']:
			return self.clickHandler(watch, args, watch['launch']) # coolest usage of scope ever
		elif watch['linkdetect']:
			return self.clickHandler(watch, args)
	
	def get_name(self):
		return self.plugin_name

	def add_click_handler(self, handler):
		self.mumbles_notify.add_click_handler(self.plugin_name, handler)
	
	def get_icon(self, icon_name):
		if not icon_name:
			return None
		
		icon = os.path.join(os.path.expanduser('~'), '.mumbles', 'icons', icon_name)
		if os.path.isfile(icon):
			return icon

		icon = os.path.join(PLUGIN_DIR_USER, 'icons', icon_name)
		if os.path.isfile(icon):
			return icon

		icon = os.path.join(PLUGIN_DIR, 'icons', icon_name)
		if os.path.isfile(icon):
			return icon

		return None
	
	def Error(self, title, message, second_pass=False):
		if not second_pass: # we need to be two frames back
	 		dbus_interface = 'org.mumblesproject.Mumbles' # fake incoming signal :)
	 		path = '/org/mumblesproject/Mumbles'
	 		signal_name = 'Error'
			self.Error(title, message, True)
			return
		self.notify(title, message)
	
 	def open_uri(self, uri): # open with default app
 		try:
	 		mime_type = gnomevfs.get_mime_type(uri)
	 		application = gnomevfs.mime_get_default_application(mime_type)
	 		os.system(application[2] + ' "' + uri + '" &')
	 	except:
			self.Error('Error opening URI', 'Maybe an invalid URI was specified?\n"%s"' % uri )
 	
 	def launch_exec(self, launch): # spawn independent process
		if launch.count(' '):
			cmd, args = launch.split(' ',1)
			args = ['']+args.split(' ') # iirc first arg should be sys.argv[0] (file path) hmm...
			os.spawnvp(os.P_NOWAIT, cmd, args)
		else:
		 	os.spawnlp(os.P_NOWAIT, launch)
	
	def striphtml(self, message):
		return re.compile('<[^>]+>').sub(' ',message)

	def unescape(self, s):
		s = s.replace("&lt;", "<")
		s = s.replace("&gt;", ">")
		s = s.replace("&apos;", "'")
		s = s.replace("&quot;", '"')
		# this must be last:
		s = s.replace("&amp;", "&")
		return s
