#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Notifier
#
#------------------------------------------------------------------------

import math
import time

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
			'use_system_colors' : 0,
			'color' : None,

			# spacing between notifications
			'spacing' : 10,

			# icon options
			'icon_x_pos' : 10,
			'icon_y_pos' : 30,

			# text formatting
			'text_title_width' : 250,
			'text_title_height' : 20,
			'text_title_font' : 'Sans',
			'text_title_color' : None,
			'text_title_size' : 10,
			'text_title_padding_left' : 15,
			'text_title_padding_right' : 5,
			'text_title_padding_upper' : 4,
			'text_title_padding_lower' : 0,

			'text_message_width' : 250,
			'text_message_height' : 60,
			'text_message_font' : 'Sans',
			'text_message_color' : None,
			'text_message_size' : 8,
			'text_message_padding_left' : 40,
			'text_message_padding_right' : 5,
			'text_message_padding_upper' : 0,
			'text_message_padding_lower' : 10 
		}

		self.xml_config_array = {
			'width'  : ['width', 'int'],
			'height' : ['height', 'int'],
			'use_system_colors' : ['use_system_colors', 'int'],
			'color'  : ['color', 'string'],
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

		self.visible = {} # keep track of visible mumbles
		self.win_placement = {} # keep track of visible mumble placement for sliding
		self.slide_tracking = {}
		
		
		self.offscreen = []
		
		self.timeout_list = {}
		self.paused = False

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
			node_a = xml_item.getElementsByTagName(outerNodeName)
			if node_a:
				node = xml_item.getElementsByTagName(outerNodeName)[0]
				if node.nodeType == Node.ELEMENT_NODE:
					if type(xml_config[node.nodeName]) is dict:
						self.process_xml_options(xml_config[node.nodeName], node)
					else:
						if xml_config[node.nodeName][1] == 'int':
							try:
								self.options.set_option(CONFIG_MT, xml_config[node.nodeName][0], int(node.firstChild.nodeValue))
							except:
								raise Exception("Warning: Invalid value for option %s. Expected integer." %(xml_config[node.nodeName][0]))
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
				self.close(widget); # don't remove widget.window >_<

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

		if self.options.get_option(CONFIG_MT, 'use_system_colors'):
			theme_style = gtk.Invisible().get_style()
			background_color = theme_style.bg[gtk.STATE_NORMAL]
			font_color = theme_style.fg[gtk.STATE_NORMAL]
		else:
			background_color = gtk.gdk.color_parse('#000')
			font_color = gtk.gdk.color_parse('#fff')

		if (self.options.get_option(CONFIG_MT, 'color') is not None):
			background_color = gtk.gdk.color_parse(self.options.get_option(CONFIG_MT, 'color'))

		try:
			cur_alpha = int(self.options.get_option(CONFIG_MN, 'notification_alpha'))
		except:
			print "Warning: Invalid value of %s for notification_alpha. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_alpha'))
			cur_alpha = 100
		alpha = float(cur_alpha)/100

		# divide by max color (as float) to get correct value in 0-1 range
		# what's the const for this...?
		font_color_t = [font_color.red / 65535.0, font_color.green / 65535.0, font_color.blue / 65535.0, 1]
		background_color_t = [background_color.red / 65535.0, background_color.green / 65535.0, background_color.blue / 65535.0, alpha]

		if self.__alpha_available:
			cr.set_source_rgba(*background_color_t)
		else:
			cr.set_source_color(background_color)

		cr.set_operator(cairo.OPERATOR_SOURCE)

		# Draw the background
		background_image = os.path.join(THEMES_DIR, self.options.get_option(CONFIG_MN, 'theme'), 'bground.svg')
		if not os.path.exists(background_image):
			background_image = os.path.join(THEMES_DIR, self.options.get_option(CONFIG_MN, 'theme'), 'bground.png')

		background_mask = os.path.join(THEMES_DIR, self.options.get_option(CONFIG_MN, 'theme'), 'bgmask.svg')
		if not os.path.exists(background_mask):
			background_mask = os.path.join(THEMES_DIR, self.options.get_option(CONFIG_MN, 'theme'), 'bgmask.png')

		if not os.path.exists(background_image):
			background_image = None
			background_mask = os.path.join(THEMES_DIR, 'default', 'bgmask.svg')

		pixbuf= None
		if (background_image and os.path.exists(background_image)):
			pixbuf = gtk.gdk.pixbuf_new_from_file(background_image)

		maskpixbuf = None
		if os.path.exists(background_mask):
			if os.path.exists(background_mask): maskpixbuf = gtk.gdk.pixbuf_new_from_file(background_mask)
			
		if maskpixbuf:
			pixmap, image_mask = maskpixbuf.render_pixmap_and_mask()
			widget.window.shape_combine_mask(image_mask, 0, 0)
			if self.__alpha_available:
				cr.set_source_rgba(*background_color_t)
			cr.paint()
			# not sure how to keep the background image (color) w/o calling
			# create again...
			if background_image is not None:
				cr = widget.window.cairo_create()

		if pixbuf:
			if background_mask is None:
				cr = widget.window.cairo_create()
			cr.set_source_pixbuf(pixbuf, 0, 0)
			cr.paint()
		else:
			cr.rectangle(0, 0, self.options.get_option(CONFIG_MT, 'width'), self.options.get_option(CONFIG_MT, 'height'))
			cr.fill()

		# add plugin image
		if not image:
			image = os.path.join(UI_DIR, 'mumbles.svg')
		try: plugin_image = gtk.gdk.pixbuf_new_from_file(image)
		except: plugin_image = None
		if plugin_image:
			new_image = plugin_image.scale_simple(28, 28, gtk.gdk.INTERP_BILINEAR)  # FIX THIS TO BE CONFIGURED IN THE THEME (instead of hardcoded)
			if not new_image: print 'Warning: Out of memory?'
			else: plugin_image = new_image
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
		p_layout_title.set_wrap(pango.WRAP_CHAR)
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

		if (self.options.get_option(CONFIG_MT, 'text_title_color') is not None):
			fc = self.options.get_option(CONFIG_MT, 'text_title_color')
			c = self.convert_hex_to_rgb(fc)
			cr.set_source_rgba(c[0], c[1], c[2])
		else:
			cr.set_source_rgba(*font_color_t)
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
		#p_fdesc.set_weight(pango.WEIGHT_BOLD)

		p_layout_message.set_font_description(p_fdesc)
		p_layout_message.set_text(message)

		cr.rectangle(0, 0, right_edge, (upper_edge + lower_edge))
		cr.clip()
		cr.move_to(left_edge, upper_edge)

		cr.set_source_rgba(1, 1, 1)
		cr.show_layout(p_layout_message)

		if (self.options.get_option(CONFIG_MT, 'text_message_color') is not None):
			fc = self.options.get_option(CONFIG_MT, 'text_message_color')
			c = self.convert_hex_to_rgb(fc)
			cr.set_source_rgba(c[0], c[1], c[2])
		else:
			cr.set_source_rgba(*font_color_t)
		cr.show_layout(p_layout_message)

		return False

	def screen_changed(self, widget, old_screen=None):        
		screen = widget.get_screen()

		# check if the widget supports alpha channels
		if widget.is_composited():
			colormap = screen.get_rgba_colormap()
			self.__alpha_available = True
		else:
			colormap = screen.get_rgb_colormap()
			self.__alpha_available = False
			
		# Now we have a colormap appropriate for the widget, use it
		widget.set_colormap(colormap)
    
		return False

	def close(self, win):
		self.close_alert(win)

	def close_timeout(self, win):
		if not win in self.visible: return
		self.visible[win] -= 1
		if not self.visible[win] < 1: return
		self.close_alert(win)
		self.close_cleanup()
	
	def close_cleanup(self):
		try:
			v_slide = int(self.options.get_option(CONFIG_MN,'vertical_sliding_enabled'))
		except:
			print 'Warning: Invalid value of %s for vertical_sliding_enabled. Falling back to default value.' %(self.options.get_option(CONFIG_MN,'vertical_sliding_enabled'))
			v_slide = 0
		
		try:
			cur_direction =  int(self.options.get_option(CONFIG_MN, 'notification_direction'))
		except:
			print "Warning: Invalid value of %s for notification_direction. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_direction'))
			cur_direction = CONFIG_NOTIFY_DIRECTION_DOWN

		if not v_slide or not self.win_placement: return

		# adjust window position by direction and placement
		# preferences and how many notifications are active
		spacing = self.options.get_option(CONFIG_MT, 'spacing')

		notify_height = self.options.get_option(CONFIG_MT, 'height')

		temp_placement = {}
		for win in self.win_placement:
			temp_placement[self.win_placement[win]] = win
		keysort = temp_placement.keys()
		keysort.sort()

		max_i = 0

		for n_index in keysort:
			win = temp_placement[n_index]
			if n_index == 0 or not n_index == self.win_placement[win]: continue
			i = self.vslide_alert(win)
			max_i = max(max_i, i)

		if cur_direction == CONFIG_NOTIFY_DIRECTION_DOWN:
			if max_i == 0:
				new_y = PANEL_HEIGHT
			else:
				new_y = PANEL_HEIGHT + (notify_height + spacing) * max_i
		else:
			if max_i == 0:
				new_y = gtk.gdk.screen_height() - (notify_height + spacing + PANEL_HEIGHT)
			else:
				new_y = gtk.gdk.screen_height() - ((notify_height + spacing) * (max_i+1) + PANEL_HEIGHT)
		self.__current_y = new_y
		#self.__n_index = max_i
		#self.__n_active = max_i
	
	def vslide_alert(self, win):
		if win in self.offscreen and not win == self.offscreen[0]: return # removes flood problem
		try:
			cur_direction =  int(self.options.get_option(CONFIG_MN, 'notification_direction'))
		except:
			print "Warning: Invalid value of %s for notification_direction. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_direction'))
			cur_direction = CONFIG_NOTIFY_DIRECTION_DOWN

		try:
			cur_placement = int(self.options.get_option(CONFIG_MN,'notification_placement'))
		except:
			print "Warning: Invalid value of %s for notification_placement. Falling back to default value." %(self.options.get_option(CONFIG_MN,'notification_placement'))
			cur_placement = CONFIG_NOTIFY_PLACEMENT_RIGHT
		
		spacing = self.options.get_option(CONFIG_MT, 'spacing')
		notify_height = self.options.get_option(CONFIG_MT, 'height')
		
		if cur_placement == CONFIG_NOTIFY_PLACEMENT_RIGHT:
			new_x = (gtk.gdk.screen_width()-self.options.get_option(CONFIG_MT, 'width')-spacing)
		else:
			new_x = spacing
			
		n_index = self.win_placement[win]
		for i in xrange(n_index):
			if not i in self.win_placement.values():
				self.win_placement[win] = i
				if cur_direction == CONFIG_NOTIFY_DIRECTION_DOWN:
					if i == 0:
						new_y = PANEL_HEIGHT
					else:
						new_y = PANEL_HEIGHT + (notify_height + spacing) * i
				else:
					if i == 0:
						new_y = gtk.gdk.screen_height() - (notify_height + spacing + PANEL_HEIGHT)
					else:
						new_y = gtk.gdk.screen_height() - ((notify_height + spacing) * (i+1) + PANEL_HEIGHT)
				self.smooth_move(win, new_x, new_y, inc=30)
				if win in self.offscreen:
					if not ((new_y + spacing) < 0 or (new_y + notify_height - spacing) > gtk.gdk.screen_height()):
						self.offscreen.remove(win)
						self.init_close_timeout(win)
				return i
		x, new_y = win.get_position()
		if not x == new_x: self.smooth_move(win, new_x, new_y)
		return 0
	
	def close_alert(self, win):
		if not win in self.visible: return
		
		try:
			h_slide = int(self.options.get_option(CONFIG_MN,'horizontal_sliding_enabled'))
		except:
			print 'Warning: Invalid value of %s for horizontal_sliding_enabled. Falling back to default value.' %(self.options.get_option(CONFIG_MN,'horizontal_sliding_enabled'))
			h_slide = 0
		
		
		try:
			fading = self.options.get_option(CONFIG_MN, 'fading_enabled')
		except:
			print "Warning: Invalid value of %s for fading_enabled. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fading_enabled'))
			fading = False
		if fading:
			try:
				fade_duration = int(self.options.get_option(CONFIG_MN, 'fade_duration'))
			except:
				print "Warning: Invalid value of %s for fade_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fade_duration'))
				fade_duration = 300
			try:
				fade_steps = int(self.options.get_option(CONFIG_MN, 'fade_steps'))
			except:
				print "Warning: Invalid value of %s for fade_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fade_steps'))
				fade_steps = 20
		
		# if time out was triggered, destroy the gtk.Window
		# otherwise, handling event call back from gtk.gdk.Window, so temporarily hide it # we don't need to anymore because it keeps track in self.visible
		#try:
		#	# decrease number of active windows if it's still visible
		#	if win.window.is_visible():
		#		self.__n_active -= 1
		#	if h_slide: self.close_slide_out(win)
		#	else: self.destroy(win)
		#except:
		#	# decrease number of active windows
		#	self.__n_active -= 1
		#	#win.hide()
		#	if h_slide: self.close_slide_out(win)
		#	else: self.destroy(win)
		# decrease number of active windows
		self.__n_active -= 1
		# slide out or close
		if h_slide: self.close_slide_out(win)
		elif fading: self.fade_out(win, fade_duration, fade_steps)
		else: self.destroy(win)
		if win in self.win_placement: del self.win_placement[win]

		# if number of active windows is back to 0, reset starting point
		if self.__n_active == 0:
			self.__n_index = 0
	
	def close_slide_out(self, win):
		if win in self.win_placement: del self.win_placement[win]
		try:
			cur_placement = int(self.options.get_option(CONFIG_MN,'notification_placement'))
		except:
			print "Warning: Invalid value of %s for notification_placement. Falling back to default value." %(self.options.get_option(CONFIG_MN,'notification_placement'))
			cur_placement = CONFIG_NOTIFY_PLACEMENT_RIGHT
		x, y = win.get_position()
		xs, ys = win.get_size()
		if cur_placement == CONFIG_NOTIFY_PLACEMENT_RIGHT:
			xm = x + xs
		else:
			xm = x - xs
		self.slide_tracking[win] = -1
		self.smooth_move(win, xm, y, callback=self.destroy, track=-1)
	
	def destroy(self, win):
		win.window.destroy()
		if win in self.win_placement: del self.win_placement[win]
		del self.visible[win]

	def replace_alert(self, win, plugin_name, name, message, image=None, click_handler=None):
		if not win in self.visible: return self.alert(plugin_name, name, message, image, click_handler)
		win.connect('expose-event', self.expose, name, message, image)
		self.visible[win] += 1

		# show window for a defined about of time
		#try: cur_duration = int(self.options.get_option(CONFIG_MN, 'notification_duration'))
		#except:
		#	print "Warning: Invalid value of %s for notification_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_duration'))
		#	cur_duration = 5
		self.init_close_timeout(win)
		#source_id = gobject.timeout_add(cur_duration*1000, self.close_timeout, win)

		win.queue_draw() # tell the widget to be redrawn
		return win
	
	def smooth_move(self, win, dest_x, dest_y, inc=50, callback=None, track=0):
		x, y = win.get_position()
		if dest_x == x and dest_y == y: return
		#win.move(x, y)
		gobject.timeout_add(20, self.move_timeout, win, (dest_x, dest_y), track, inc, callback)
	
	def move_timeout(self, win, coords, track=0, inc=50, callback=None):
		if not win in self.visible: return
		if not win in self.slide_tracking:
			self.slide_tracking[win] = 0
		else:
			if track == 0 and not self.slide_tracking[win] == -1:
				self.slide_tracking[win] += 1
				track = self.slide_tracking[win]
			elif not track == self.slide_tracking[win]:
				return # there's a newer slide taking place
		dx, dy = coords
		x, y = win.get_position()
		if abs(dx-x) < 100 and abs(dy-y) < 100:
			inc = inc/1.3
		if x < dx:
			if x+inc < dx: x += inc
			else: x = dx
		elif x > dx:
			if x-inc > dx: x -= inc
			else: x = dx
		if y < dy:
			if y+inc < dy: y += inc
			else: y = dy
		elif y > dy:
			if y-inc > dy: y -= inc
			else: y = dy
		win.move(int(x), int(y))
		if dx == x and dy == y:
			if win in self.slide_tracking:
				if track == self.slide_tracking[win]:
					del self.slide_tracking[win]
			if callback: callback(win)
			return
		gobject.timeout_add(20, self.move_timeout, win, (dx, dy), track, inc, callback)
	
	def pause(self):
		return # borked
		self.paused = True
		now = time.time()*1000
		for win in self.visible:
			self.visible[win] += 1
		for win in self.timeout_list:
			self.timeout_list[win] = abs(self.timeout_list[win]-now)
	
	def resume(self):
		return # borked
		self.paused = False
		now = time.time()*1000
		for win in self.timeout_list:
			if not win in self.offscreen:
				gobject.timeout_add(int(self.timeout_list[win]), self.close_timeout, win)
				self.timeout_list[win] += now
	
	def hovered(self, widget, event):
		x, y = widget.get_position()
		widget.move(x-10, y)
	
	def unhovered(self, widget, event):
		x, y = widget.get_position()
		widget.move(x+10, y)
	
	def fade_in(self, win, time, steps, max_alpha):
		gobject.timeout_add(time/steps, self.fade_step_in, win, time, steps, 1, max_alpha)

	def fade_step_in(self, win, time, steps, cur, max_alpha):
		win.set_opacity(float(cur)/steps*max_alpha/100)
		if cur < steps: gobject.timeout_add(time/steps, self.fade_step_in, win, time, steps, cur+1, max_alpha)
	
	def fade_out(self, win, time, steps):
		alpha = win.get_opacity()
		gobject.timeout_add(time/steps, self.fade_step_out, win, time, steps, steps, alpha)

	def fade_step_out(self, win, time, steps, cur, max_alpha):
		win.set_opacity(float(cur)/steps*max_alpha)
		if cur > 0: gobject.timeout_add(time/steps, self.fade_step_out, win, time, steps, cur-1, max_alpha)
		else: self.destroy(win)
	
	def init_close_timeout(self, win):
		now = time.time()*1000
		try:
			cur_duration = int(self.options.get_option(CONFIG_MN, 'notification_duration'))
		except:
			print "Warning: Invalid value of %s for notification_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_duration'))
			cur_duration = 5
		timeout = cur_duration*1000
		if self.paused:
			self.timeout_list[win] = timeout
		else:
			gobject.timeout_add(timeout, self.close_timeout, win)
			self.timeout_list[win] = now+timeout

	def alert(self, plugin_name, name, message, image=None, click_handler=None, widget=None):
		try:
			cur_alpha = int(self.options.get_option(CONFIG_MN, 'notification_alpha'))
		except:
			print "Warning: Invalid value of %s for notification_alpha. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_alpha'))
			cur_alpha = 100
		try:
			fading = self.options.get_option(CONFIG_MN, 'fading_enabled')
		except:
			print "Warning: Invalid value of %s for fading_enabled. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fading_enabled'))
			fading = False
		if fading:
			try:
				fade_duration = int(self.options.get_option(CONFIG_MN, 'fade_duration'))
			except:
				print "Warning: Invalid value of %s for fade_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fade_duration'))
				fade_duration = 300
			try:
				fade_steps = int(self.options.get_option(CONFIG_MN, 'fade_steps'))
			except:
				print "Warning: Invalid value of %s for fade_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'fade_steps'))
				fade_steps = 20
				
		# figure out whether we are replacing the window or making a new one
		replacing = False
		if widget:
			if hasattr(widget, 'get_position'):
				if widget in self.visible:
					replacing = True
					#print replacing

		# setup window
		#win = gtk.Window(gtk.WINDOW_TOPLEVEL)
		win = gtk.Window(gtk.WINDOW_POPUP)

		win.set_title('Mumbles')
		win.add_events(gtk.gdk.BUTTON_PRESS_MASK)

		win.connect('delete-event', gtk.main_quit)
		win.connect('expose-event', self.expose, name, message, image)
		win.connect('screen-changed', self.screen_changed)

		try:
			if click_handler:
				win.connect('button-press-event', click_handler, plugin_name)
			else:
				win.connect('button-press-event', self.__click_handlers[plugin_name], plugin_name)
		except:
			win.connect('button-press-event', self.clicked)
		
		#win.connect('enter-notify-event', self.hovered)
		#win.connect('leave-notify-event', self.unhovered)

		win.set_app_paintable(True)
		win.set_decorated(False)
		win.set_skip_taskbar_hint(True)
		win.set_skip_pager_hint(True)
		win.set_accept_focus(False)
		win.set_keep_above(True)
		if fading: win.set_opacity(0)
		else: win.set_opacity(float(cur_alpha)/100)
		win.stick()

		# initialize for the current display
		self.screen_changed(win)
		width = self.options.get_option(CONFIG_MT, 'width')
		win.resize( self.options.get_option(CONFIG_MT, 'width'),
			self.options.get_option(CONFIG_MT, 'height'))

		# adjust window position by direction and placement
		# preferences and how many notifications are active
		spacing = self.options.get_option(CONFIG_MT, 'spacing')

		notify_height = self.options.get_option(CONFIG_MT, 'height')

		try:
			cur_direction =  int(self.options.get_option(CONFIG_MN, 'notification_direction'))
		except:
			print "Warning: Invalid value of %s for notification_direction. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_direction'))
			cur_direction = CONFIG_NOTIFY_DIRECTION_DOWN

		if cur_direction == CONFIG_NOTIFY_DIRECTION_DOWN:
			y_start = 0

			if self.__n_index == 0:
				new_y = PANEL_HEIGHT
			else:
				new_y = self.__current_y + notify_height + spacing

		else:
			y_start = gtk.gdk.screen_height() - notify_height - PANEL_HEIGHT
			if self.__n_index == 0:
				new_y = gtk.gdk.screen_height() - notify_height - PANEL_HEIGHT
			else:
				new_y = self.__current_y - notify_height - spacing

		if not replacing:
			self.__current_y = new_y

		try:
			cur_placement = int(self.options.get_option(CONFIG_MN,'notification_placement'))
		except:
			print "Warning: Invalid value of %s for notification_placement. Falling back to default value." %(self.options.get_option(CONFIG_MN,'notification_placement'))
			cur_placement = CONFIG_NOTIFY_PLACEMENT_RIGHT
		if cur_placement == CONFIG_NOTIFY_PLACEMENT_RIGHT:
			new_x = (gtk.gdk.screen_width()-self.options.get_option(CONFIG_MT, 'width')-spacing)
		else:
			new_x = spacing
		if replacing:
			null_x, new_y = widget.get_position()
			
		try:
			h_slide = int(self.options.get_option(CONFIG_MN,'horizontal_sliding_enabled'))
		except:
			print 'Warning: Invalid value of %s for horizontal_sliding_enabled. Falling back to default value.' %(self.options.get_option(CONFIG_MN,'horizontal_sliding_enabled'))
			h_slide = 0
		
		try:
			v_slide = int(self.options.get_option(CONFIG_MN,'vertical_sliding_enabled'))
		except:
			print 'Warning: Invalid value of %s for vertical_sliding_enabled. Falling back to default value.' %(self.options.get_option(CONFIG_MN,'vertical_sliding_enabled'))
			v_slide = 0
		
		if h_slide:
			if cur_placement == CONFIG_NOTIFY_PLACEMENT_RIGHT:
				win.move(new_x+width, new_y)
			else:
				win.move(new_x-width, new_y)
		else:
			win.move(new_x, new_y)
		

		# increase number of active notifications
		n_index = self.__n_index
		if not replacing:
			self.__n_index += 1
			self.__n_active += 1

		# show window for a defined about of time
		#try:
		#	cur_duration = int(self.options.get_option(CONFIG_MN, 'notification_duration'))
		#except:
		#	print "Warning: Invalid value of %s for notification_duration. Falling back to default value." %(self.options.get_option(CONFIG_MN, 'notification_duration'))
		#	cur_duration = 5
		#source_id = gobject.timeout_add(cur_duration*1000, self.close_timeout, win)
		if ((new_y + spacing) < 0 or (new_y + notify_height - spacing) > gtk.gdk.screen_height()) and v_slide:
			self.offscreen.append(win)
		else:
			self.init_close_timeout(win)

		# finally show (and trigger the expose event)
		self.visible[win] = 1 # number of timeouts
		self.win_placement[win] = n_index
		win.show_all()
		#if replacing: widget.hide()
		if fading:
			self.fade_in(win, fade_duration, fade_steps, cur_alpha)
		if h_slide:
			if v_slide: self.smooth_move(win, new_x, new_y, callback=self.vslide_alert) #self.vslide_alert(win)
			else: self.smooth_move(win, new_x, new_y)
		elif v_slide: self.vslide_alert(win)
		#print self.__n_active

		return win
