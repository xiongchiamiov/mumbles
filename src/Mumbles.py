#!/usr/bin/env python
#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Main Class
#
#------------------------------------------------------------------------

import os
import sys
import pkg_resources

import gtk.glade

import egg.trayicon

import dbus
import dbus.service
if getattr(dbus,'version',(0,0,0)) >= (0,41,0):
	import dbus.glib

from OptionsHandler import *

from MumblesGlobals import *
from MumblesNotify import *
from MumblesOptions import *
from MumblesDBus import *


class Mumbles(object):

	def __init__(self, verbose):
		self.__verbose = verbose
		self.__bus = None
		self.__mumbles_notify = None
		self.__plugins = {}
		self.__available_plugins = {}
		self.__panel_glade = PANEL_GLADE_FILE
		self.__preferences_glade = PREFERENCES_GLADE_FILE
		self.__options = None
		self.__about = None
		self.__preferences = None

	def __on_NameOwnerChanged(self, name, old_owner, new_owner):
		if name in self.__available_plugins and new_owner:

			if self.__verbose:
				print "NameOwnerChanged: %s" %(name)

			plugin = self.__plugins.get(name)

			try:
				plugin.create(self.__mumbles_notify, self.__bus)
				if self.__verbose:
					print "Successfully loaded %s plugin" %(plugin.get_name())
			except:
				if self.__verbose:
					print "Warning: Unable to load plugin for %s" %(name)

	# return True when delete-event is fired to prevent
	# window from being destroyed
	def __delete_event(self, widget, event):
		return True

	def __menu_activate(self, widget, event):
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
		self.__options.set_option('mumbles', 'notification_placement', self.__preferences.get_widget('combo_screen_placement').get_active())
		self.__options.set_option('mumbles', 'notification_direction', self.__preferences.get_widget('combo_direction').get_active())
		self.__options.set_option('mumbles', 'notification_duration', self.__preferences.get_widget('spin_duration').get_value_as_int())
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
		self.__preferences.get_widget('combo_screen_placement').set_active(int(self.__options.get_option('mumbles', 'notification_placement')))
		self.__preferences.get_widget('combo_direction').set_active(int(self.__options.get_option('mumbles', 'notification_direction')))
		self.__preferences.get_widget('spin_duration').set_value(int(self.__options.get_option('mumbles', 'notification_duration')))


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
					plugin = plugin_cls()
					self.__plugins[plugin.get_dbus_name()] = plugin

			for plugin_dbus_name, plugin in self.__plugins.items():

				# keep a list of all available plugins
				self.__available_plugins[plugin_dbus_name] = True

				# load plugins that have running services
				if plugin_dbus_name in self.__dbus_iface.ListNames():
					try:
						plugin.create(self.__mumbles_notify, self.__bus)
						if self.__verbose:
							print "Successfully loaded %s plugin" %(plugin.get_name())
					except:
						if self.__verbose:
							print "Warning: Unable to load plugin for %s" %(plugin_dbus_name)
		except:
			if self.__verbose:
				print "Error: Unable to load plugins"


	def __get_widget_by_name(self, glade_file, name, signals=None):
		w = gtk.glade.XML(glade_file, name)
		if signals:
			w.signal_autoconnect(signals)
		return w.get_widget(name)

	def __create_panel_applet(self):
		signals = {
			"on_panel_clicked" : self.__menu_activate,
		}
		eventbox_widget = self.__get_widget_by_name(self.__panel_glade, 'mumbles_eventbox', signals)

		tray = egg.trayicon.TrayIcon("Mumbles")
		tray.add(eventbox_widget)
		tray.show_all()

	def main(self):

		try:
			self.__bus = dbus.SessionBus()
		except:
			if self.__verbose:
				print "Error: DBus appears to not be running."
			return False

		# create callback to load plugin when its service is started
		dbus_object = self.__bus.get_object(DBUS_NAME, DBUS_OBJECT)
		self.__dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)
		self.__dbus_iface.connect_to_signal("NameOwnerChanged", self.__on_NameOwnerChanged)

		self.__options = MumblesOptions()
		if os.path.isfile(self.__options.filename):
			# if config file exists, load it
			self.__options.load()
		else:
			# if no config file create one
			# using defaults from MumblesOptions
			self.__options.create_file(self.__options.options)

		self.__mumbles_notify = MumblesNotify(self.__options)

		name = dbus.service.BusName(MUMBLES_DBUS_NAME,bus=self.__bus)
		obj = MumblesDBus(name, self.__mumbles_notify)

		self.__load_mumbles_plugins()

		self.__create_panel_applet()

		self.__loop = gobject.MainLoop()
		if self.__verbose:
			print "Listening..."
		self.__loop.run()


if __name__ == '__main__':
	mumbles = Mumbles(verbose=False)
	sys.exit(mumbles.main())

