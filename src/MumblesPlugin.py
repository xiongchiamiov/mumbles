#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Base 
#------------------------------------------------------------------------

from MumblesGlobals import *
from MumblesDBus import *
from OptionsHandler import *
import dbus
import dbus.service

class MumblesPlugin(OptionsHandler):

	plugin_name = ''
	plugin_bus = None

	def __init__(self, session_bus, options = None, verbose = False):
		self._verbose = verbose 

		self._outputs = {}

		self._options = None
		OptionsHandler.__init__(self, self.plugin_name)
		self.init_options()
		if options:
			self._merge_options(options)

		self.session_bus = session_bus
		dbus_object = self.session_bus.get_object(DBUS_NAME, DBUS_OBJECT)
		dbus_iface = dbus.Interface(dbus_object, DBUS_NAME)
		path = MUMBLES_DBUS_OBJECT+'/'+self.plugin_name
		# only 1 object per plugin
		try:
			name = dbus.service.BusName(MUMBLES_DBUS_NAME, bus=self.session_bus)
			self.plugin_bus = MumblesPluginDBus(name, path)
		except KeyError:
			pass


	def get_name(self):
		return self.plugin_name

	def init_options(self):
		pass

	def attach_output_plugin(self, plugin):
		#TODO: check that this output plugin is enabled for self (input plugin)
		if self._verbose:
			print "Attaching output plugin %s to %s" %(plugin.get_name(), self.get_name())
		self._output_attach(plugin)

	def _input_alert(self):

		#send alert msg received to the dbus
		if self.plugin_bus:
			self.plugin_bus.SentNotification()

		# notify the output plugins we have an alert
		#TODO: (should they pick up the dbus signal from above rather than calling plugin.alert()?
		for name, plugins in self._outputs.iteritems():
			for plugin in plugins:
				try:
					plugin.alert(self.alert_object)
					if plugin.plugin_bus:
						plugin.plugin_bus.ReceivedNotification()
				except Exception, e:
					if self._verbose:
						print "Exception found alerting to %s (%s)" %(plugin.get_name(), e)

	def _input_add_click_handler(self, handler):
		pass

	def _output_attach(self, plugin):
		p_name = plugin.get_name()
		if p_name not in self._outputs:
			self._outputs[p_name] = []
		self._outputs[p_name].append(plugin)
