#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Base 
#------------------------------------------------------------------------

from MumblesGlobals import *
from MumblesDBus import *
import dbus
import dbus.service

class MumblesPlugin(object):

	plugin_name = ''
	_verbose = False
	_outputs = {}

	def __init__(self, session_bus, options = None, verbose = False):
		#to-do: do we want to hang on to options here?
		self._verbose = verbose 
		self.session_bus = session_bus

		dbus_object = self.session_bus.get_object(DBUS_NAME, DBUS_OBJECT)
		dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)
		path = MUMBLES_DBUS_OBJECT+'/'+self.plugin_name
		name = dbus.service.BusName(MUMBLES_DBUS_NAME, bus=self.session_bus)
		self.plugin_bus = MumblesPluginDBus(name, path)

	def get_name(self):
		return self.plugin_name

	def attach_output_plugin(self, plugin):
		#to-do: check that this output plugin is enabled for self (input plugin)
		if self._verbose:
			print "Attaching output plugin %s to %s" %(plugin.get_name(), self.get_name())
		self._output_attach(plugin)


	def _input_alert(self):
		#send alert msg received to the dbus
		self.plugin_bus.SentNotification()

		# notify the output plugins we have an alert
		#to-do: (should they pick up the dbus signal from above rather than calling plugin.alert()?
		for name, plugin in self._outputs.iteritems():
			try:
				plugin.alert(self.alert_object)
				plugin.plugin_bus.ReceivedNotification()
			except:
				if self._verbose:
					print "Exception found alerting to %s" %(plugin.get_name())

	def _input_add_click_handler(self, handler):
		pass

	def _output_attach(self, plugin):
		self._outputs[plugin.get_name()] = plugin
