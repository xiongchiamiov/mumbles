#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Options Handler
#
#------------------------------------------------------------------------

from MumblesGlobals import *
from OptionsHandler import *

class MumblesOptions(OptionsFileHandler):

	_daemon = 0
	_verbose = 0

	def __init__(self):
		OptionsFileHandler.__init__(self)

		# General Settings 
		mumbles = self.add_section('mumbles', 'Mumbles Settings')
		mumbles.add_option(BooleanOption('daemon',
			self._daemon,
			'Show in panel',
			'Use mumbles panel applet'))
		mumbles.add_option(BooleanOption('verbose',
			self._verbose,
			'Verbose',
			'Run mumbles in verbose mode'))

		plugins = self.add_section('plugins', 'Mumbles Plugins')
		inputs = plugins.add_section('inputs', 'Mumbles Input Plugins')
		outputs = plugins.add_section('outputs', 'Mumbles Output Plugins')
		mapping = plugins.add_section('mapping', 'Mumbles Plugin Mappings')

	def init_default_plugins(self):
		# Inputs
		inputs = self.get_section('plugins/inputs')
		generic = inputs.add_section(name='input', description='GenericMumblesInput', id=0)
		generic.set_enabled(True)

		# Outputs
		outputs = self.get_section('plugins/outputs')
		sp = outputs.add_section(name='output', description='SimplePrintMumblesOutput', id=0)
		sp.set_enabled(True)
		sp.add_option(BooleanOption('advanced',
			True,
			'Advanced',
			'Detailed Simple Print Output'))

		# TODO add mapping helper function to do this bit automatically
		# Mapping
		maps = self.get_section('plugins/maps')
		generic_in = maps.add_section(name='input', description='', id=0)
		generic_out = generic_in.add_section(name='output', description='', id=0)
