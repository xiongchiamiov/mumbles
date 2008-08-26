#!/usr/bin/env python
#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Main Class
#
#------------------------------------------------------------------------

import os
import getopt 
import sys
import pkg_resources
import gtk.glade
import threading
import gobject

USE_EGG_TRAYICON = True 
try:
	import pygtk
	pygtk.require('2.0')
	if gtk.pygtk_version[0] == 2 and gtk.pygtk_version[1] >= 10:
		USE_EGG_TRAYICON = False
except:
	pass
if USE_EGG_TRAYICON:
	import egg.trayicon 

import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
	import dbus.glib
from getpass import getpass

from OptionsHandler import *
from MumblesGlobals import *
from MumblesOptions import *
from MumblesDBus import *
from GrowlNetwork import *


class Usage(Exception):
        def __init__(self, msg=None):
                #self.msg = 'Usage: Mumbles.py [-h] [-v] [-d] [-g|-x] [-p]'
		app = sys.argv[0]
		if msg != 'help':
			self.msg = app+': Invalid options. Try --help for usage details.'
		else:
			self.msg = \
				app+": Desktop notifications for the Gnome desktop.\n" \
				"Copyright (C) 2007 dot_j <dot_j@mumbles-project.org>\n\n" \
				"Usage: mumbles [options]\n\n" \
				"-h, --help\n" \
				"\tPrint a summary of the command-line usage of "+app+".\n" \
				"-v, --verbose\n" \
				"\tEnable debug messages.\n" \
				"-d, --daemon\n" \
				"\tRun in daemon mode without a panel applet.\n" \
				"-g, --enable-growl-network\n" \
				"\tEnable growl network support.\n" \
				"-p {password}, --password {password}\n" \
				"\tUse the supplied password for growl network support.\n" \
				"-x, --disable-growl-network\n" \
				"\tDisable growl network support.\n"

class Mumbles(object):

	def __init__(self):
		self.__bus = None
		self.__plugins = {PLUGIN_TYPE_INPUT:{}, PLUGIN_TYPE_OUTPUT:{}}
		self.__available_plugins = {PLUGIN_TYPE_INPUT:{}, PLUGIN_TYPE_OUTPUT:{}}
		self.__panel_glade = PANEL_GLADE_FILE
		self.__preferences_glade = PREFERENCES_GLADE_FILE
		self.__options = None
		self.__themes = None
		self.__about = None
		self.__preferences = None
		self.__tray = None
		self.__verbose = True

	# return True when delete-event is fired to prevent
	# window from being destroyed
	def __delete_event(self, widget, event):
		return True

	# menu activation for gtk.StatusIcon
	def __menu_activate(self, status_icon, button, activate_time):
		signals = {
			"on_preferences_activate" : self.__menu_preferences_activate,
			"on_about_activate" : self.__menu_about_activate,
			"on_quit_activate" : self.__menu_quit_activate
		}
		self.__get_widget_by_name(self.__panel_glade, 'mumbles_menu', signals).popup(None, None, None, button, activate_time)

	# menu activation for egg.trayicon
	def __egg_menu_activate(self, widget, event=None):
		if event.button == 3:
			signals = {
				"on_preferences_activate" : self.__menu_preferences_activate,
				"on_about_activate" : self.__menu_about_activate,
				"on_quit_activate" : self.__menu_quit_activate
			}
			menu_widget = self.__get_widget_by_name(self.__panel_glade, "mumbles_menu", signals)
			menu_widget.set_screen(widget.get_screen())
			menu_widget.popup(None, None, None, event.button, event.time)

	def __preferences_ok(self, widget):

		# get updated settings
		self.__options.set_option(CONFIG_MN, 'notification_placement', self.__preferences.get_widget('combo_screen_placement').get_active())
		self.__options.set_option(CONFIG_MN, 'notification_direction', self.__preferences.get_widget('combo_direction').get_active())
		self.__options.set_option(CONFIG_MN, 'notification_duration', self.__preferences.get_widget('spin_duration').get_value_as_int())
		self.__options.set_option(CONFIG_MN, 'theme', self.__preferences.get_widget('combo_theme').get_active_text())

		self.__options.set_option(CONFIG_M, 'growl_network_enabled', int(self.__preferences.get_widget('check_growl_network').get_active()))
		self.__options.set_option(CONFIG_M, 'growl_network_password', self.__encrypt(self.__preferences.get_widget('entry_growl_password').get_text()))

		self.__options.save()
		#TODO: handle plugin options update here
		#self.__mumbles_notify.set_options(self.__options)
		self.__growl_server.update(self.__options.get_option(CONFIG_M, 'growl_network_enabled'), self.__decrypt(self.__options.get_option(CONFIG_M, 'growl_network_password')))

		self.__preferences_close(None)

	def __preferences_close(self, widget, event=None):
		self.__preferences_window.hide()
		return True

	def __growl_network_toggled(self, widget, event=None):
		if widget.get_active():
			self.__preferences.get_widget('label_growl_password').set_sensitive(True)
			self.__preferences.get_widget('entry_growl_password').set_editable(True)
		else:
			self.__preferences.get_widget('label_growl_password').set_sensitive(False)
			self.__preferences.get_widget('entry_growl_password').set_editable(False)
		return True

	def __menu_preferences_activate(self, widget):

		signals = {
			"on_ok_clicked" : self.__preferences_ok,
			"on_cancel_clicked" : self.__preferences_close,
			"on_preferences_destroy" : self.__preferences_close,
			"on_preferences_delete" : self.__preferences_close,
			"on_check_growl_network_toggled" : self.__growl_network_toggled
		}

		self.__preferences = gtk.glade.XML(self.__preferences_glade, "mumbles_preferences")
		self.__preferences.signal_autoconnect(signals)

		self.__preferences_window = self.__preferences.get_widget("mumbles_preferences")

		# populate with existing settings (or defaults)
		try:
			self.__preferences.get_widget('combo_screen_placement').set_active(int(self.__options.get_option(CONFIG_MN, 'notification_placement')))
		except:
			self.__preferences.get_widget('combo_screen_placement').set_active(CONFIG_NOTIFY_PLACEMENT_RIGHT)
			if self.__verbose:
				print "Warning: Unable to set option for notification_placement. Falling back to default value."

		try:
			self.__preferences.get_widget('combo_direction').set_active(int(self.__options.get_option(CONFIG_MN, 'notification_direction')))
		except:
			self.__preferences.get_widget('combo_direction').set_active(CONFIG_NOTIFY_DIRECTION_DOWN)
			if self.__verbose:
				print "Warning: Unable to set option for notification_direction. Falling back to default value."

		try:
			self.__preferences.get_widget('spin_duration').set_value(int(self.__options.get_option(CONFIG_MN, 'notification_duration')))
		except:
			self.__preferences.get_widget('spin_duration').set_value(5)
			if self.__verbose:
				print "Warning: Unable to set option for notification_duration. Falling back to default value."

		combo_theme = self.__preferences.get_widget('combo_theme')
		selected_theme = self.__options.get_option(CONFIG_MN, 'theme')
		index = 0
		active = 0
		for i, theme_name in enumerate(self.__themes):
			combo_theme.append_text(theme_name)
			if theme_name == selected_theme:
				active = i
		combo_theme.set_active(active)

		try:
			self.__preferences.get_widget('check_growl_network').set_active(int(self.__options.get_option(CONFIG_M, 'growl_network_enabled')))
		except:
			self.__preferences.get_widget('check_growl_network').set_active(0)
			if self.__verbose:
				print "Warning: Unable to set option for growl network enabled. Falling back to default value."
		passwd = self.__decrypt(self.__options.get_option(CONFIG_M, 'growl_network_password'))
		self.__preferences.get_widget('entry_growl_password').set_text(passwd)


	def __about_close(self, widget, event=None):
		self.__about.hide()

	def __menu_about_activate(self, widget):
		signals = {
			"on_about_response" : self.__about_close,
			"on_about_destroy" : self.__about_close,
			"on_about_delete" : self.__delete_event,
		}
		if not self.__about:
			self.__about = self.__get_widget_by_name(self.__panel_glade, "mumbles_about", signals)

		self.__about.show()

	def __menu_quit_activate(self, widget):
		self.__loop.quit()

	def __get_available_plugins(self, plugin_type, dirlist):
		try:
			for d in dirlist:
				pkg_resources.working_set.add_entry(d)
			pkg_env = pkg_resources.Environment(dirlist)

			for name in pkg_env:
				egg = pkg_env[name][0]
				egg.activate()
				for name in egg.get_entry_map(ENTRY_POINT):
					entry_point = egg.get_entry_info(ENTRY_POINT, name)
					plugin_cls = entry_point.load()
					self.__available_plugins[plugin_type][name] = plugin_cls

		except Exception, e:
			if self.__verbose:
				print "Error: Unable to load plugins %s" %(e)


	def __load_mumbles_plugins(self, plugin_type, dirlist):

		if True:
		#try:

			# init list of plugins available
			self.__get_available_plugins(plugin_type, dirlist)

			# get plugin options from the xml
			config_options = {}
			section = self.__options.get_section('plugins/'+plugin_type)
			for s in section.get_sections():
				name = s.get_description()
				if name not in config_options:
					config_options[name] = {}
				id = s.get_id()
				config_options[name][id] = s

			# get plugin mappings from the xml
			if plugin_type == PLUGIN_TYPE_OUTPUT:
				map_list = {}
				map_section = self.__options.get_section('plugins/maps')
				for ins in map_section.get_sections():
					input_id = ins.get_id()
					if input_id not in map_list:
						map_list[input_id] = []
					for outs in ins.get_sections():
						output_id = outs.get_id()
						if output_id not in map_list[input_id]:
							map_list[input_id].append(output_id)


			for plugin_name, plugin_cls in self.__available_plugins[plugin_type].iteritems():

				# if there are no options from the xml, use the plugin defaults
				# TODO - disable these
				if plugin_name not in config_options:
					config_options[plugin_name] = {0: None}

				for index, opts in config_options[plugin_name].iteritems():

					#try:
					if True:
						plugin_cls = self.__available_plugins[plugin_type][plugin_name]
						plugin = plugin_cls(self.__bus, options=opts, verbose=self.__verbose)

						if self.__verbose:
							print "Processing plugin %s:" %(plugin.get_name())

						# attach output plugings to our inputs
						if plugin_type == PLUGIN_TYPE_OUTPUT and plugin.is_enabled():
							input_plugins = self.__plugins[PLUGIN_TYPE_INPUT]
							for name, inputs in input_plugins.iteritems():
								for input in inputs:
									# check that this input plugin
									# is enabled and mapped to this output
									if input.get_id() is not None and input.is_enabled():
										if plugin.get_id() in map_list[input.get_id()]:
											input.attach_output_plugin(plugin)

						# add plugin to our list
						p_name = plugin.get_name()
						if p_name not in self.__plugins[plugin_type]:
							self.__plugins[plugin_type][p_name] = []
						self.__plugins[plugin_type][p_name].append(plugin)

						if self.__verbose:
							if plugin.is_enabled():
								print "Successfully loaded\n"
							else:
								print "Not enabled\n"
					#except KeyError:
						#print "Error: No available plugin %s found." %(plugin_name)
		#except:
			#if self.__verbose:
				#print "Warning: Unable to load plugin for %s" %(name)
				#print "\t %s for value: %s" %(sys.exc_info()[:2])

	# at least it's better than plain text...
	def __encrypt(self, plain):
		ret = ''
		for i in range(len(plain)): 
				ret += chr(ord(plain[i])+i+1)
		return ret

	def __decrypt(self, enc_pass):
		ret = ''
		if enc_pass:
			for i in range(len(enc_pass)): 
					ret += chr(ord(enc_pass[i])-i-1)
		return ret



	def __get_widget_by_name(self, glade_file, name, signals=None):
		w = gtk.glade.XML(glade_file, name)
		if signals:
			w.signal_autoconnect(signals)
		return w.get_widget(name)

	def __create_panel_applet(self):
		if USE_EGG_TRAYICON:
			signals = {
				"on_panel_clicked" : self.__egg_menu_activate,
			}
			eventbox_widget = self.__get_widget_by_name(self.__panel_glade, 'mumbles_eventbox', signals)

			self.__tray = egg.trayicon.TrayIcon("Mumbles")
			self.__tray.add(eventbox_widget)
			self.__tray.show_all()
		else:
			self.__tray = gtk.StatusIcon()
			panel_icon = self.__get_widget_by_name(self.__panel_glade, 'panel_icon_image').get_pixbuf()
			self.__tray.set_from_pixbuf(panel_icon)
			self.__tray.connect("popup_menu", self.__menu_activate) 
			self.__tray.set_visible(True)

	def __get_themes(self):
		themes = ['default']
		t = [THEMES_DIR, THEMES_DIR_USER]
		for t_path in t:
			if os.path.isdir(t_path):
				tmp_list = os.listdir(t_path)
				tmp_list.sort()
				for theme_name in tmp_list:
					if os.path.isdir(os.path.join(t_path, theme_name)) and theme_name[:1] != '.' and theme_name not in themes:
						themes.append(theme_name)
		return themes

	def main(self, argv=None):

		check_password = False;

		# create mumbles main options handler
		# loaded with defaults
		self.__options = MumblesOptions()

		# if config file exists, load it
		# if no config file exists, attempt to create
		# one and use the defaults from MumblesOptions
		if os.path.isfile(self.__options.get_filename()):
			self.__options.load()
		else:
			self.__options.init_default_plugins()
			self.__options.create_file()

		self.__themes = self.__get_themes()

		if argv is None:
			argv = sys.argv

		try:
			try:
				opts, args = getopt.getopt(
					sys.argv[1:],
					"hdv",
					["help", "daemon", "verbose"])
					#"hdvgpx",
					#["help", "daemon", "verbose", "enable-growl-network", "password", "disable-growl-network"])
			except getopt.GetoptError:
				raise Usage()

			for o, a in opts:
				if o in ("-h", "--help"):
					raise Usage('help')
				elif o in ("-v", "--verbose"):
					self.__options.set_option('mumbles/verbose', 1)
				elif o in ("-d", "--daemon"):
					self.__options.set_option('mumbles/daemon', 1)
				#elif o in ("-g", "--enable-growl-network"):
					#self.__options.set_enabled('networking/growl', True)
				#elif o in ("-p", "--password"):
					#check_password = True;
				#elif o in ("-x", "--disable-growl-network"):
					#self.__options.set_enabled('networking/growl', False)
				else:
					raise Usage()
		except Usage, err:
			print >> sys.stderr, err.msg
			return 2

		self.__verbose = False
		try:
			self.__verbose = self.__options.get_option('mumbles/verbose')
		except:
			self.__verbose = False

		try:
			self.__bus = dbus.SessionBus()
		except:
			if self.__verbose:
				print "Error: DBus appears to not be running."
			return False

		# create callback to load plugin when its service is started
		#dbus_object = self.__bus.get_object(DBUS_NAME, DBUS_OBJECT)
		#self.__dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)
		#name = dbus.service.BusName(MUMBLES_DBUS_NAME,bus=self.__bus)
		#obj = MumblesDBus(name)

		dirlist = [PLUGIN_DIR_INPUT_CORE, PLUGIN_DIR_INPUT_THIRDPARTY, PLUGIN_DIR_INPUT_USER]
		self.__load_mumbles_plugins(PLUGIN_TYPE_INPUT, dirlist)

		dirlist = [PLUGIN_DIR_OUTPUT_CORE, PLUGIN_DIR_OUTPUT_THIRDPARTY, PLUGIN_DIR_OUTPUT_USER]
		self.__load_mumbles_plugins(PLUGIN_TYPE_OUTPUT, dirlist)

		if not self.__options.get_option('mumbles/daemon'):
			self.__create_panel_applet()
		elif self.__verbose:
			print "Starting Mumbles in daemon mode"

		self.__loop = gobject.MainLoop()
		gobject.threads_init()

		# TODO move to input plugin
		'''
		# setup growl network handler
		passwd = None
		passwd = self.__decrypt(self.__options.get_option('networking/growl/password'))
		if check_password:
			passwd = getpass()
		# start growl network listener
		self.__growl_server = GrowlServer(('', GROWL_UDP_PORT), growlIncoming, passwd)
		self.__growl_thread = threading.Thread(target = self.__growl_server.serve_forever) 
		self.__growl_thread.setDaemon(True)
		self.__growl_thread.start()

		if self.__options.is_enabled('networking/growl'):
			if self.__verbose:
				print "Starting Growl Network Support..."
			self.__growl_server.update(True, passwd)
		'''


		print "DEBUG"
		#self.__options.print_content()

		if self.__verbose:
			print "Mumbles is Listening..."

		self.__loop.run()


if __name__ == '__main__':
	mumbles = Mumbles()
	sys.exit(mumbles.main())