#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Notifier
#
#------------------------------------------------------------------------

import os
import pango
import cairo

import gobject

import gtk
import pygtk
pygtk.require('2.0')

import xml.dom.minidom
from xml.dom.minidom import Node

from MumblesGlobals import *
from OptionsHandler import *

# used for notification placement as they will be auto moved below/above the panels
# so expect both panels to be showing and place accordingly
PANEL_HEIGHT = 25

class MumblesNotifyOptions(OptionsHandler):

	def __init__(self):
		OptionsHandler.__init__(self)

		self.options[CONFIG_MN] = {
			# placement and direction of notifications
			'notification_placement' : CONFIG_NOTIFY_PLACEMENT_RIGHT,
			'notification_direction' : CONFIG_NOTIFY_DIRECTION_DOWN,

			# how long to show the notifications (seconds)
			'notification_duration' : 5,

			# theme directory
			'theme' : 'default'
		}

		self.options[CONFIG_MT] = {

			# dimenstions of the notification area
			'width' : 250,
			'height' : 80,

			# spacing between notifications
			'spacing' : 10,

			# icon options
			'icon_x_pos' : 10,
			'icon_y_pos' : 30,

			# text formatting
			'text_title_width' : 250,
			'text_title_height' : 20,
			'text_title_font' : 'Sans',
			'text_title_color' : '#fff',
			'text_title_size' : 10,
			'text_title_padding_left' : 15,
			'text_title_padding_right' : 5,
			'text_title_padding_upper' : 4,
			'text_title_padding_lower' : 0,

			'text_message_width' : 250,
			'text_message_height' : 60,
			'text_message_font' : 'Sans',
			'text_message_color' : '#fff',
			'text_message_size' : 8,
			'text_message_padding_left' : 40,
			'text_message_padding_right' : 5,
			'text_message_padding_upper' : 0,
			'text_message_padding_lower' : 10 
		}

		self.xml_config_array = {
			'width'  : ['width', 'int'],
			'height' : ['height', 'int'],
			'spacing' : ['spacing', 'int'],
			'icon' : {
				'x_pos' : ['icon_x_pos', 'int'],
				'y_pos' : ['icon_y_pos', 'int']
			},
			'text' : {
				'title' : {
					'font' : {
						'family' : ['text_title_font', 'string'],
						'color'  : ['text_title_color', 'string'],
						'size'   : ['text_title_size', 'int']
					},
					'width'  : ['text_title_width', 'int'],
					'height' : ['text_title_height', 'int'],
					'padding' : {
						'left'  : ['text_title_padding_left', 'int'],
						'right'  : ['text_title_padding_right', 'int'],
						'upper' : ['text_title_padding_upper', 'int'],
						'lower' : ['text_title_padding_lower', 'int']
					}
				},
				'message' : {
					'font' : {
						'family' : ['text_message_font', 'string'],
						'color'  : ['text_message_color', 'string'],
						'size'   : ['text_message_size', 'int'],
					},
					'width'  : ['text_message_width', 'int'],
					'height' : ['text_message_height', 'int'],
					'padding' : {
						'left'  : ['text_message_padding_left', 'int'],
						'right'  : ['text_message_padding_right', 'int'],
						'upper' : ['text_message_padding_upper', 'int'],
						'lower' : ['text_message_padding_lower', 'int']
					}
				}
			}
		}



class MumblesNotify(object):

	def __init__(self, options = None):

		# get default notification options
		self.options = MumblesNotifyOptions()

		# if options were passed, update default options with those
		if options:
			self.options.add_options(options)

		theme_name = self.options.get_option(CONFIG_MN, 'theme')

		theme_xml = os.path.join(THEMES_DIR_USER, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, 'default', 'config.xml')

		self.add_options_from_config(theme_name, theme_xml)

		# keep track of how many notices deep we are
		self.__n_index = 0

		# keep track of how many active notices there are
		self.__n_active = 0

		self.__click_handlers = {}

		# keep track of last notification vertical placement
		self.__current_y = 0

	def set_options(self, new_options):
		self.options.add_options(new_options)
		theme_name = self.options.get_option(CONFIG_MN, 'theme')
		theme_xml = os.path.join(THEMES_DIR_USER, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, 'default', 'config.xml')
		self.add_options_from_config(theme_name, theme_xml)

	def process_xml_options(self, xml_config, xml_item):

		for outerNodeName in xml_config:
			#for node in xml_item.getElementsByTagName(outerNodeName):
			node = xml_item.getElementsByTagName(outerNodeName)[0]
			if node.nodeType == Node.ELEMENT_NODE:
				if type(xml_config[node.nodeName]) is dict:
					self.process_xml_options(xml_config[node.nodeName], node)
				else:
					if xml_config[node.nodeName][1] == 'int':
						self.options.set_option(CONFIG_MT, xml_config[node.nodeName][0], int(node.firstChild.nodeValue))
					else:
						self.options.set_option(CONFIG_MT, xml_config[node.nodeName][0], node.firstChild.nodeValue)


	def add_options_from_config(self, theme_name, theme_xml):

		# create xml document
		if not os.path.exists(theme_xml):
			raise Exception('"%s" theme config file not found: "%s".' %(theme_name, theme_xml))

		try:
			doc = xml.dom.minidom.parse(theme_xml)
		except:
			raise Exception('Invalid XML in "%s" theme config file: "%s".' %(theme_name,  theme_xml))

		# get root node
		root = doc.firstChild
		if not root or root.nodeName != CONFIG_MT:
			raise Exception('Missing or invalid rootnode "CONFIG_MT" in "%s" theme config file: "%s".' %(theme_name, theme_xml))

		root_theme_name = root.getAttribute('name')
		if not root_theme_name:
			raise Exception('No name for theme defined in "%s".' %(theme_xml))
		elif root_theme_name != theme_name and root_theme_name != 'default':
			raise Exception('Theme direcotry name "%s" does not match name defined in XML "%s".' %(theme_name, root_theme_name))

		self.process_xml_options(self.options.xml_config_array, root)


	def add_click_handler(self, plugin_name, click_handler):
		self.__click_handlers[plugin_name] = click_handler

	def clicked(self, widget, event, plugin_name = None):
		try:
			self.__click_handlers[plugin_name](widget, event, plugin_name)
		except:
			if event.button == 3:
				self.close(widget.window);

	def convert_hex_to_rgb(self, hex_color):
		if hex_color[0] == '#':
			hex_color = hex_color[1:]
		if len(hex_color) != 6:
			if len(hex_color) != 3:
				err = "Color #%s is not in #rrggbb or #rgb format" %(hex_color)
				raise ValueError, err
			else:
				hex_color = hex_color[0]*2+hex_color[1]*2+hex_color[2]*2

		ret = []
		r = hex_color[:2]
		g = hex_color[2:4]
		b = hex_color[4:]

		for c in (r, g, b):
			ret.append((int(c, 16) / 255.0))

		return ret

	def expose(self, widget, event, title, message, image):

		cr = widget.window.cairo_create()

        	# restrict to window area
		cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		cr.clip()

		if self.__alpha_available:
			cr.set_source_rgba(0.0, 0.0, 0.0, 0.0)
		else:
			cr.set_source_rgb(0.0, 0.0, 0.0)

		cr.set_operator(cairo.OPERATOR_SOURCE)

		# Draw the background
		background_image = os.path.join(THEMES_DIR, self.options.get_option(CONFIG_MN, 'theme'), 'bground.png')
		default_background_image = os.path.join(THEMES_DIR, 'default', 'bground.png')

		if os.path.exists(background_image):
			pixbuf = gtk.gdk.pixbuf_new_from_file(background_image)
		elif os.path.exists(default_background_image):
			pixbuf = gtk.gdk.pixbuf_new_from_file(default_background_image)
		else:
			pixbuf = None
			
		if pixbuf:
			cr.set_source_pixbuf(pixbuf, 0, 0)
			cr.paint()
		else:
			cr.rectangle(0, 0, self.options.get_option(CONFIG_MT, 'width'), self.options.get_option(CONFIG_MT, 'height'))
			cr.fill()

		# add plugin image
		if not image:
			image = os.path.join(UI_DIR, 'mumbles.png')
		plugin_image = gtk.gdk.pixbuf_new_from_file(image)
		if plugin_image:
			widget.window.draw_pixbuf(None, plugin_image, 0, 0, self.options.get_option(CONFIG_MT, 'icon_x_pos'), self.options.get_option(CONFIG_MT, 'icon_y_pos'))

		cr.reset_clip()

		# add the title
		text_title_width = self.options.get_option(CONFIG_MT, 'text_title_width')
		text_title_height = self.options.get_option(CONFIG_MT, 'text_title_height')
		text_title_padding_left = self.options.get_option(CONFIG_MT, 'text_title_padding_left')
		text_title_padding_right = self.options.get_option(CONFIG_MT, 'text_title_padding_right')
		text_title_padding_upper = self.options.get_option(CONFIG_MT, 'text_title_padding_upper')
		text_title_padding_lower = self.options.get_option(CONFIG_MT, 'text_title_padding_lower')

		left_edge = (0 + text_title_padding_left)
		upper_edge = (0 + text_title_padding_upper)
		right_edge = (text_title_width - text_title_padding_right)
		lower_edge = (text_title_height - text_title_padding_lower)

		p_layout_title = cr.create_layout()
		p_layout_title.set_wrap(pango.WRAP_WORD)
		p_layout_title.set_width((right_edge - left_edge) * pango.SCALE)

		p_fdesc = pango.FontDescription()
		p_fdesc.set_family_static(self.options.get_option(CONFIG_MT, 'text_title_font'))
		p_fdesc.set_size(self.options.get_option(CONFIG_MT, 'text_title_size') * pango.SCALE)
		p_fdesc.set_weight(pango.WEIGHT_BOLD)

		p_layout_title.set_font_description(p_fdesc)
		p_layout_title.set_text(title)

		cr.rectangle(0, 0, right_edge, (upper_edge + lower_edge))
		cr.clip()
		cr.move_to(left_edge, upper_edge)

		c = self.convert_hex_to_rgb(self.options.get_option(CONFIG_MT, 'text_title_color'))
		cr.set_source_rgba(c[0], c[1], c[2])
		cr.show_layout(p_layout_title)

		cr.reset_clip()

		# add the message
		text_message_width = self.options.get_option(CONFIG_MT, 'text_message_width')
		text_message_height = self.options.get_option(CONFIG_MT, 'text_message_height')
		text_message_padding_left = self.options.get_option(CONFIG_MT, 'text_message_padding_left')
		text_message_padding_right = self.options.get_option(CONFIG_MT, 'text_message_padding_right')
		text_message_padding_upper = self.options.get_option(CONFIG_MT, 'text_message_padding_upper')
		text_message_padding_lower = self.options.get_option(CONFIG_MT, 'text_message_padding_lower')

		left_edge = (0 + text_message_padding_left)
		upper_edge = (text_message_padding_upper + text_title_height) # here start the top edge at the bottom of the title
		right_edge = (text_message_width - text_message_padding_right)
		lower_edge = (text_message_height - text_message_padding_lower)

		p_layout_message = cr.create_layout()
		p_layout_message.set_wrap(pango.WRAP_WORD)
		p_layout_message.set_width((right_edge - left_edge) * pango.SCALE)

		p_fdesc = pango.FontDescription()
		p_fdesc.set_family(self.options.get_option(CONFIG_MT, 'text_message_font'))
		p_fdesc.set_size(self.options.get_option(CONFIG_MT, 'text_message_size') * pango.SCALE)
		p_fdesc.set_weight(pango.WEIGHT_BOLD)

		p_layout_message.set_font_description(p_fdesc)
		p_layout_message.set_text(message)

		cr.rectangle(0, 0, right_edge, (upper_edge + lower_edge))
		cr.clip()
		cr.move_to(left_edge, upper_edge)

		cr.set_source_rgba(1, 1, 1)
		cr.show_layout(p_layout_message)

		c = self.convert_hex_to_rgb(self.options.get_option(CONFIG_MT, 'text_message_color'))
		cr.set_source_rgba(c[0], c[1], c[2])
		cr.show_layout(p_layout_message)

		return False

	def screen_changed(self, widget, old_screen=None):
        
		# To check if the display supports alpha channels, get the colormap
		screen = widget.get_screen()
		try:
			colormap = screen.get_rgba_colormap()
			self.__alpha_available = True
		except:
			colormap = None

		if colormap == None:
			self.__alpha_available = False
			try:
				colormap = screen.get_rgb_colormap()
				self.__alpha_available = False
			except:
				colormap = None

		# Now we have a colormap appropriate for the screen, use it
		widget.set_colormap(colormap)
    
		return False

	def close(self, win):
		self.close_alert(win)
	
	def close_alert(self, win):
		# if time out was triggered, destroy the gtk.Window
		# otherwise, handling event call back from gtk.gdk.Window, so temporarily hide it
		try:
			# decrease number of active windows if it's still visible
			if win.window.is_visible():
				self.__n_active -= 1
			win.window.destroy()
		except:
			# decrease number of active windows
			self.__n_active -= 1
			win.hide()

		# if number of active windows is back to 0, reset starting point
		if self.__n_active == 0:
			self.__n_index = 0

    
	def alert(self, plugin_name, name, message, image=None):
		# setup window
		win = gtk.Window(gtk.WINDOW_TOPLEVEL)

		win.set_title('Mumbles')
		win.add_events(gtk.gdk.BUTTON_PRESS_MASK)

		win.connect('delete-event', gtk.main_quit)
		win.connect('expose-event', self.expose, name, message, image)
		win.connect('screen-changed', self.screen_changed)

		try:
			win.connect('button-press-event', self.__click_handlers[plugin_name], plugin_name)
		except:
			win.connect('button-press-event', self.clicked)

		win.set_app_paintable(True)
		win.set_decorated(False)
		win.set_skip_taskbar_hint(True)
		win.set_skip_pager_hint(True)
		win.set_accept_focus(False)
		win.set_keep_above(True)
		win.stick()

		# initialize for the current display
		self.screen_changed(win)
		win.resize( self.options.get_option(CONFIG_MT, 'width'),
			self.options.get_option(CONFIG_MT, 'height'))

		# adjust window position by direction and placement
		# preferences and how many notifications are active
		spacing = self.options.get_option(CONFIG_MT, 'spacing')

		notify_height = self.options.get_option(CONFIG_MT, 'height')

		if int(self.options.get_option(CONFIG_MN, 'notification_direction')) == CONFIG_NOTIFY_DIRECTION_DOWN:

			if self.__n_index == 0:
				new_y = PANEL_HEIGHT
			else:
				new_y = self.__current_y + notify_height + spacing

		else:
			if self.__n_index == 0:
				new_y = gtk.gdk.screen_height() - notify_height - PANEL_HEIGHT
			else:
				new_y = self.__current_y - notify_height - spacing

		self.__current_y = new_y

		if int(self.options.get_option(CONFIG_MN,'notification_placement')) == CONFIG_NOTIFY_PLACEMENT_RIGHT:
			new_x = (gtk.gdk.screen_width()-self.options.get_option(CONFIG_MT, 'width')-spacing)
		else:
			new_x = spacing 
		win.move(new_x, new_y)

		# increase number of active notifications
		self.__n_index += 1
		self.__n_active += 1

		# show window for a defined about of time
		source_id = gobject.timeout_add(int(self.options.get_option(CONFIG_MN, 'notification_duration'))*1000, self.close_alert, win)

		# finally show (and trigger the expose event)
		win.show_all()

		return True
