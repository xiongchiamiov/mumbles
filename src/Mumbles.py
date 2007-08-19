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
from MumblesNotify import *
from MumblesOptions import *
from MumblesDBus import *
from GrowlNetwork import *


class Usage(Exception):
        def __init__(self, msg=None):
                self.msg = 'Usage: Mumbles.py [-h] [-v] [-d] [-g|-x] [-p]'

class Mumbles(object):

	def __init__(self):
		self.__bus = None
		self.__mumbles_notify = None
		self.__plugins = {}
		self.__panel_glade = PANEL_GLADE_FILE
		self.__preferences_glade = PREFERENCES_GLADE_FILE
		self.__options = None
		self.__about = None
		self.__preferences = None
		self.__tray = None

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
		self.__options.set_option('mumbles-notifications', 'notification_placement', self.__preferences.get_widget('combo_screen_placement').get_active())
		self.__options.set_option('mumbles-notifications', 'notification_direction', self.__preferences.get_widget('combo_direction').get_active())
		self.__options.set_option('mumbles-notifications', 'notification_duration', self.__preferences.get_widget('spin_duration').get_value_as_int())
		self.__options.save()

		self.__preferences_close(None)

	def __preferences_close(self, widget, event=None):
		self.__preferences_window.hide()
		return True

	def __menu_preferences_activate(self, widget):

		signals = {
			"on_ok_clicked" : self.__preferences_ok,
			"on_cancel_clicked" : self.__preferences_close,
			"on_preferences_destroy" : self.__preferences_close,
			"on_preferences_delete" : self.__preferences_close,
		}

		self.__preferences = gtk.glade.XML(self.__preferences_glade, "mumbles_preferences")
		self.__preferences.signal_autoconnect(signals)

		self.__preferences_window = self.__preferences.get_widget("mumbles_preferences")

		# populate with existing settings (or defaults)
		self.__preferences.get_widget('combo_screen_placement').set_active(int(self.__options.get_option('mumbles-notifications', 'notification_placement')))
		self.__preferences.get_widget('combo_direction').set_active(int(self.__options.get_option('mumbles-notifications', 'notification_direction')))
		self.__preferences.get_widget('spin_duration').set_value(int(self.__options.get_option('mumbles-notifications', 'notification_duration')))


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

	def __load_mumbles_plugins(self):

		try:
			pkg_resources.working_set.add_entry(PLUGIN_DIR)
			pkg_env = pkg_resources.Environment([PLUGIN_DIR])

			for name in pkg_env:
				egg = pkg_env[name][0]
				egg.activate()
				for name in egg.get_entry_map(ENTRY_POINT):
					entry_point = egg.get_entry_info(ENTRY_POINT, name)
					plugin_cls = entry_point.load()

					try:
						plugin = plugin_cls(self.__mumbles_notify, self.__bus)
						self.__plugins[plugin.get_name()] = plugin

						if self.__verbose:
							print "Successfully loaded %s plugin" %(plugin.get_name())
					except:
						if self.__verbose:
							print "Warning: Unable to load plugin for %s" %(name)
		except:
			if self.__verbose:
				print "Error: Unable to load plugins"


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

	def main(self, argv=None):

		check_password = False;

		self.__options = MumblesOptions()
		if os.path.isfile(self.__options.filename):
			# if config file exists, load it
			self.__options.load()
		else:
			# if no config file create one
			# using defaults from MumblesOptions
			self.__options.create_file(self.__options.options)

		# convert boolean values to integers
		self.__options.set_option('mumbles', 'verbosity', int(self.__options.get_option('mumbles', 'verbosity')))
		self.__options.set_option('mumbles', 'daemon', int(self.__options.get_option('mumbles', 'daemon')))
		self.__options.set_option('mumbles', 'growl_network_enabled', int(self.__options.get_option('mumbles', 'growl_network_enabled')))

        	if argv is None:
                	argv = sys.argv
        	try:
			try:
				opts, args = getopt.getopt(
					sys.argv[1:],
					"hdvgpx",
					["help", "daemon", "verbose", "enable-growl-network", "password", "disable-growl-network"])
			except getopt.GetoptError:
                               	raise Usage()

			for o, a in opts:
				if o in ("-h", "--help"):
					raise Usage()
				elif o in ("-v", "--verbose"):
					self.__options.set_option('mumbles', 'verbose', True)
				elif o in ("-d", "--daemon"):
					self.__options.set_option('mumbles', 'daemon', True)
				elif o in ("-g", "--enable-growl-network"):
					self.__options.set_option('mumbles', 'growl_network_enabled', True)
				elif o in ("-p", "--password"):
					check_password = True;
				elif o in ("-x", "--disable-growl-network"):
					self.__options.set_option('mumbles', 'growl_network_enabled', False)
				else:
					raise Usage()
        	except Usage, err:
                	print >> sys.stderr, err.msg
                	return 2

		self.__verbose = False
		if int(self.__options.get_option('mumbles', 'verbose')):
			self.__verbose = True
			self.__options.show_options()

		try:
			self.__bus = dbus.SessionBus()
		except:
			if self.__verbose:
				print "Error: DBus appears to not be running."
			return False


		# create callback to load plugin when its service is started
		dbus_object = self.__bus.get_object(DBUS_NAME, DBUS_OBJECT)
		self.__dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)

		self.__mumbles_notify = MumblesNotify(self.__options)

		name = dbus.service.BusName(MUMBLES_DBUS_NAME,bus=self.__bus)
		obj = MumblesDBus(name)

		self.__load_mumbles_plugins()

		if not self.__options.get_option('mumbles', 'daemon'):
			self.__create_panel_applet()
		elif self.__verbose:
			print "Starting Mumbles in daemon mode"

		self.__loop = gobject.MainLoop()
		gobject.threads_init()

		if self.__options.get_option('mumbles', 'growl_network_enabled'):
			passwd = None
			if check_password:
				passwd = getpass()
			# start growl network listener
			if self.__verbose:
				print "Starting Growl Network Support..."
			growl_server = GrowlServer(('', GROWL_UDP_PORT), growlIncoming, passwd)
			self.__growl_thread = threading.Thread(target = growl_server.serve_forever) 
			self.__growl_thread.setDaemon(True)
			self.__growl_thread.start()

		if self.__verbose:
			print "Mumbles is Listening..."

		self.__loop.run()


if __name__ == '__main__':
	mumbles = Mumbles()
	sys.exit(mumbles.main())
