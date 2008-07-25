#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Options Handler Parent Class
#
#------------------------------------------------------------------------

import os
from MumblesGlobals import *
from xml.dom import minidom

class Option(object):
	_name = ''
	_value = None
	_label = ''
	_tooltip = ''
	_type = None

	def __init__(self, name, value, label='', tooltip=''):
		self._name = name
		self._value = value
		self._label = label
		self._tooltip = tooltip

	def get_name(self):
		return self._name

	def get_value(self):
		return self._value

	def set_value(self, value):
		self._value = value

	def get_label(self):
		return self._label

	def get_tooltip(self):
		return self._tooltip

	def get_type(self):
		return self._type

class IntegerOption(Option):
	def __init__(self, name, value, label='', tooltip=''):
		Option.__init__(self, name, value, label, tooltip)
		self.set_value(value)
		self._type = 'integer'

	def set_value(self, value):
		self._value = int(value)

class TextOption(Option):
	def __init__(self, name, value, label='', tooltip=''):
		Option.__init__(self, name, value, label, tooltip)
		self._type = 'text'
		self.set_value(value)

class BooleanOption(Option):
	def __init__(self, name, value, label='', tooltip=''):
		Option.__init__(self, name, value, label, tooltip)
		self._type = 'boolean'
		self.set_value(value)

	def get_value(self):
		if self._value:
			return 1
		else:
			return 0

	def set_value(self, value):
		if value == 0 or value == False or int(value) == 0:
			self._value = 0
		else:
			self._value = 1

class PasswordOption(Option):
	def __init__(self, name, value, label='', tooltip=''):
		Option.__init__(self, name, value, label, tooltip)
		self._type = 'password'

	def get_value(self):
		if not self._value:
			return ''
		return self._value



class OptionsHandler(object):
	_id = None
	_name = ''
	_description = ''
	_sections = []
	_options = {}
	_new = False
	_enabled = None

	def __init__(self, name='', description='', id=None):
		self._name = name
		self._description = description

		if id is not None:
			self._id = id
		self._sections = []
		self._options = {}

	def get_name(self):
		return self._name

	def set_name(self, name):
		self._name = name

	def get_id(self):
		if self._id is None or self._id == '':
			return None
		return int(self._id)

	def set_id(self, id):
		self._id = id

	def get_description(self):
		return self._description

	def set_description(self, description):
		self._description = description

	def add_option(self, option):
		self._options[option.get_name()] = option

	def is_enabled(self, path=None):
		if not path:
			return self._enabled

		try:
			for n in self._sections:
				children = path.split('/')
				if len(children) and n.get_name() == children[0]:
					return n.get_section("/".join(children[1:]))
		except Exception, e:
			print "Error: %s" %e

		return None

	def set_enabled(self, value):
		if value:
			self._enabled = True
		else:
			self._enabled = False

	def add_section(self, name, description, id=None):
		new_section = OptionsHandler(name, description, id)
		self._sections.append(new_section)
		return new_section

	def get_sections(self):
		return self._sections

	def get_section(self, path=None):
		if not path:
			return self

		try:
			for n in self._sections:
				children = path.split('/')
				if len(children) and n.get_name() == children[0]:
					return n.get_section("/".join(children[1:]))
		except Exception, e:
			print "Error: %s" %e

		return None

	def get_option(self, path):
		try:
			if self._options[path]:
				return self._options[path].get_value()
		except:
			pass

		try:
			for n in self._sections:
				children = path.split('/')
				if len(children) and n.get_name() == children[0]:
					return n.get_option("/".join(children[1:]))
		except Exception, e:
			print "Error: %s" %e

		return None

	def set_option(self, path, value):
		children = path.split('/')
		if len(children) == 1:
			try:
				self._options[path].set_value(value)
				return True
			except Exception, e:
				print "Error: %s" %(e)
				return False

		try:
			children = path.split('/')
			for n in self._sections:
				if len(children) and n.get_name() == children[0]:
					return n.set_option("/".join(children[1:]), value)

		except Exception, e:
				print "Error: %s" %(e)
				return False

		return False


	def print_content(self, count=0):
		if self._name:
			for i in range(count):
				print "  ",
			enabled = ""
			if self.is_enabled():
				enabled = " (enabled)"
			print "%s - %s%s" %(self._name, self._description, enabled)
		if self._options:
			for name, opt in self._options.iteritems():
				for i in range(count + 1):
					print "  ",
				print "[%s::%s - %s - %s]" %(name, opt.get_value(), opt.get_label(), opt.get_tooltip())
		if self._sections:
			for n in self._sections:
				count = count + 1
				n.print_content(count)
				count = count - 1

	def _create_options_from_xml(self, parentNode):

		for node in parentNode.childNodes:
			if node.nodeType == minidom.Node.ELEMENT_NODE:

				type_attrib = node.getAttribute('type')
				id_attrib = node.getAttribute('id')
				name_attrib = node.getAttribute('name')

				enabled_attrib = node.getAttribute('enabled')
				enabled = False
				if enabled_attrib and enabled_attrib == '1':
					enabled = True

				try:
					value = node.childNodes[0].nodeValue.strip()
				except:
					value = None


				if type_attrib:
					# options
					f = False
					for name, opt in self._options.iteritems():
						if name == node.nodeName:
							opt.set_value(value)
							f = True
					if not f:
						if type_attrib == 'boolean':
							self.add_option(BooleanOption(node.nodeName, value))
						elif type_attrib == 'integer':
							self.add_option(IntegerOption(node.nodeName, value))
						elif type_attrib == 'text':
							self.add_option(TextOption(node.nodeName, value))
						elif type_attrib == 'password':
							self.add_option(PasswordOption(node.nodeName, value))
						else:
							pass
				else:
					# sections
					#TODO change "new" to some kind of id for this instance
					f = False
					for section in self._sections:
						if not section._new:
							if section.get_name() == node.nodeName:
								section._create_options_from_xml(node)
								section.set_enabled(enabled)
								f = True
					if not f:
						s = self.add_section(name=node.nodeName, description=name_attrib, id=id_attrib)
						if id_attrib is not None:
							s.set_enabled(enabled)
						s._new = True
						s._create_options_from_xml(node)

	def _merge_options(self, new_opts):

		try:
			if new_opts.is_enabled():
				self.set_enabled(True)
			self.set_id(new_opts.get_id())
		except:
			pass

		try:
			for name, opt in new_opts._options.iteritems():
				self._options[name].set_value(opt.get_value())
		except:
			pass

		try:
			for new_section in new_opts._sections:
				for section in self._sections:
					if section.get_name() == new_section.get_name():
						section._merge_options(new_section)
						enabled = new_section.is_enabled()
						if enabled is not None:
							section.set_enabled(enabled)
		except:
			pass


class OptionsFileHandler(OptionsHandler):

	_filename = CONFIG_FILE
	_dom = None

	def __init__(self):
		OptionsHandler.__init__(self)

	def get_filename(self):
		return self._filename

	def get_xml(self):
		if self._dom:
			return self._dom.toprettyxml()
		return ''

	# file handling
	def create_file(self):
		#try:
		if True:
			conf_dir = os.path.dirname(self._filename)
			if not os.path.isdir(conf_dir):
				os.mkdir(conf_dir)
			if not os.path.isfile(self._filename):
				self._dom = minidom.Document()

				self.set_name('mumbles-options')

				self.update_dom(self._dom, self)
				self.save()
		#except Exception, e:
			#raise Exception("Error: Unable to create config file:\n %s" %(e))

	def save(self):
		#try:
		if True:
			f = open(self._filename, 'w')
			f.write(self.get_xml())
			f.close()
		#except Exception, e:
			#raise Exception("Error: Unable to write config file:\n %s" %(e))

	def update_dom(self, dom, node):
		s = self._dom.createElement(node.get_name())
		id = node.get_id()
		if id is not None:
			desc = node.get_description()
			if desc:
				s.setAttribute('name', desc)
			enabled = node.is_enabled()
			if enabled is not None:
				if enabled:
					s.setAttribute('enabled', '1')
				else:
					s.setAttribute('enabled', '0')
			s.setAttribute('id', str(id))
		child = dom.appendChild(s)

		for name, opt in node._options.iteritems():
			o = self._dom.createElement(name)
			type = opt.get_type()
			if type:
				o.setAttribute('type', type)
			val = self._dom.createTextNode(str(opt.get_value()))
			o.appendChild(val)
			child.appendChild(o)

		for section in node._sections:
			self.update_dom(child, section)

	def load(self):
		#try:
		if True:
			if os.path.isfile(self._filename):
				self._dom = minidom.parse(self._filename)
				for child in self._dom.childNodes:
					if child.nodeType == minidom.Node.ELEMENT_NODE:
						childName = child.localName
						if childName != 'mumbles-options':
							raise Exception('Invalid Options XML.')

						self.set_name(childName)
						self.set_description(child.getAttribute('version'))

						for section in self._sections:
							node = child.getElementsByTagName(section.get_name())[0]
							if node.nodeType == minidom.Node.ELEMENT_NODE:
								section._create_options_from_xml(node)
					else:
						raise Exception('Invalid Options XML.')

			self._dom.unlink()
			self.update_dom(self._dom, self)

		#except Exception, e:
			#raise Exception("Error: Unable to load config file:\n %s" %(e))

