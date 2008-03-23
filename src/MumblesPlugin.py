#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Plugin Base 
#------------------------------------------------------------------------

from MumblesGlobals import *

class MumblesPlugin(object):

	plugin_name = ''
	_verbose = False
	_outputs = {}

	def __init__(self, options = None, verbose = False):
		#to-do: do we want to hang on to options here?
		self._verbose = verbose 

	def get_name(self):
		return self.plugin_name

	def attach_output_plugin(self, plugin):
		#to-do: check that this output plugin is enabled for self (input plugin)
		if self._verbose:
			print "Attaching output plugin %s to %s" %(plugin.get_name(), self.get_name())
		self._output_attach(plugin)


	def _input_alert(self):
		for name, plugin in self._outputs.iteritems():
			plugin.alert(self.alert_object)

	def _input_add_click_handler(self, handler):
		pass

	def _output_attach(self, plugin):
		self._outputs[plugin.get_name()] = plugin
