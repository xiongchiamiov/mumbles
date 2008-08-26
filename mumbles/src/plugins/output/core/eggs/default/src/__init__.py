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

from MumblesOutputPlugin import *

# used for notification placement as they will be auto moved below/above the panels
# so expect both panels to be showing and place accordingly
PANEL_HEIGHT = 25

class DefaultMumblesOutputTheme(OptionsFileHandler):

	def __init__(self, theme_name):
		OptionsFileHandler.__init__(self)

		theme_xml = os.path.join(THEMES_DIR_USER, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, theme_name, 'config.xml')
		if not os.path.isfile(theme_xml):
			theme_xml = os.path.join(THEMES_DIR, 'default', 'config.xml')
		self._filename = theme_xml

		# TODO load em from the file!
		# TODO move these exceptions to general OptionsFileHandler
		'''
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
		'''

		# General Settings 
		self.add_option(IntegerOption('width',
			250,
			'Width',
			'Notification width'))
		self.add_option(IntegerOption('height',
			80,
			'Height',
			'Notification height'))
		self.add_option(IntegerOption('spacing',
			10,
			'Spacing',
			'Notification spacing'))
		self.add_option(TextOption('image',
			'bground.png',
			'Background Image',
			'Background Image'))
		self.add_option(BooleanOption('use_system_colors',
			True,
			'Use Sytem Colors',
			'Use the default system colors'))
		self.add_option(TextOption('color',
			'#000',
			'Background Color',
			'Background Color'))
		self.add_option(IntegerOption('transparency',
			50,
			'Transparency',
			'Percentage Transparent'))

		# icon options
		icon = self.add_section('icon', 'Icon options')
		icon.add_option(IntegerOption('xpos',
			10,
			'X-Position',
			'Horizontal Position'))
		icon.add_option(IntegerOption('ypos',
			30,
			'Y-Position',
			'Vertical Position'))
		icon.add_option(IntegerOption('width',
			20,
			'Width',
			'Icon width'))
		icon.add_option(IntegerOption('height',
			20,
			'Height',
			'Icon height'))

		# text & message options:
		text = self.add_section('text', 'Display Text Options')
		title = text.add_section('title', 'Title Formatting')
		message = text.add_section('message', 'Message Formatting')

		title.add_option(IntegerOption('width',
			250,
			'Width',
			'Title width'))
		message.add_option(IntegerOption('width',
			250,
			'Width',
			'Message width'))

		title.add_option(IntegerOption('height',
			20,
			'Height',
			'Title height'))
		message.add_option(IntegerOption('height',
			60,
			'Height',
			'Message height'))

		# font
		t_font = title.add_section('font', 'Title font settings')
		m_font = message.add_section('font', 'Message font settings')
		t_font.add_option(TextOption('family',
			'Free Sans',
			'Font Family',
			'Title font family'))
		m_font.add_option(TextOption('family',
			'Free Sans',
			'Font Family',
			'Message font family'))
		t_font.add_option(TextOption('color',
			'#fff',
			'Font Color',
			'Title font color'))
		m_font.add_option(TextOption('color',
			'#fff',
			'Font Color',
			'Message font color'))
		t_font.add_option(IntegerOption('size',
			10,
			'Font Size',
			'Title font size'))
		m_font.add_option(IntegerOption('size',
			8,
			'Font Size',
			'Message font size'))

		# padding
		t_padding = title.add_section('padding', 'Title padding')
		m_padding = message.add_section('padding', 'Message font padding')

		t_padding.add_option(IntegerOption('left',
			15,
			'Left',
			'Title left padding'))
		m_padding.add_option(IntegerOption('left',
			40,
			'Left',
			'Message left padding'))
		t_padding.add_option(IntegerOption('right',
			5,
			'Right',
			'Title right padding'))
		m_padding.add_option(IntegerOption('right',
			5,
			'Right',
			'Message right padding'))
		t_padding.add_option(IntegerOption('upper',
			4,
			'Upper',
			'Title upper padding'))
		m_padding.add_option(IntegerOption('upper',
			0,
			'Upper',
			'Message upper padding'))
		t_padding.add_option(IntegerOption('lower',
			0,
			'Lower',
			'Title lower padding'))
		m_padding.add_option(IntegerOption('lower',
			10,
			'Lower',
			'Message lower padding'))




class DefaultMumblesOutput(MumblesOutputPlugin):

	plugin_name = "DefaultMumblesOutput"

	def __init__(self, session_bus, options = None, verbose = False):
		MumblesOutputPlugin.__init__(self, session_bus, options, verbose)

		# keep track of how many notices deep we are
		self._n_index = 0

		# keep track of how many active notices there are
		self._n_active = 0

		self._click_handlers = {}

		# keep track of last notification vertical placement
		self._current_y = 0

		self._theme = DefaultMumblesOutputTheme(self.get_option('theme'))

	def init_options(self):
		self.add_option(IntegerOption('placement',
			CONFIG_NOTIFY_PLACEMENT_RIGHT,
			'Placement',
			'Screen placement of the notifications'))

		self.add_option(IntegerOption('direction',
			CONFIG_NOTIFY_DIRECTION_DOWN,
			'Direction',
			'Stacking direction of the notifications'))

		self.add_option(IntegerOption('duration',
			10,
			'Duration',
			'Duration of the notifications'))

		self.add_option(TextOption('theme',
			'default',
			'Theme',
			'Notification theme'))
		
	def add_click_handler(self, plugin_name, click_handler):
		self._click_handlers[plugin_name] = click_handler

	def clicked(self, widget, event, plugin_name = None):
		try:
			self._click_handlers[plugin_name](widget, event, plugin_name)
		except:
			if event.button == 3:
				self.close(widget.window);

	def expose(self, widget, event, title, message, image):

		cr = widget.window.cairo_create()

        	# restrict to window area
		cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
		cr.clip()

		if self._theme.get_option('use_system_colors'):
			theme_style = gtk.Invisible().get_style()
			background_color = theme_style.bg[gtk.STATE_NORMAL]
		else:
			background_color = gtk.gdk.color_parse(self._theme.get_option('color'))

		if self._alpha_available:
			# divide by max color (as float) to get correct value in 0-1 range
			cr.set_source_rgba(background_color.red / 65535.0,
				background_color.green / 65535.0,
				background_color.blue / 65535.0,
				((100 - self._theme.get_option('transparency'))/100.0))
		else:
			cr.set_source_color(background_color)

		cr.set_operator(cairo.OPERATOR_SOURCE)

		# Draw the background
		background_image = None
		theme_background_image_name = self._theme.get_option('image')
		if theme_background_image_name:
			background_image = os.path.join(THEMES_DIR_USER, self.get_option('theme'), theme_background_image_name)
			if not os.path.isfile(background_image):
				background_image = os.path.join(THEMES_DIR, self.get_option('theme'), theme_background_image_name)
			if not os.path.isfile(background_image):
				background_image = os.path.join(THEMES_DIR, 'default', theme_background_image_name)

		if background_image is not None and os.path.exists(background_image):
			pixbuf = gtk.gdk.pixbuf_new_from_file(background_image)
		else:
			pixbuf = None
			
		if pixbuf:
			cr.set_source_pixbuf(pixbuf, 0, 0)
			cr.paint()
		else:
			cr.rectangle(0, 0, self._theme.get_option('width'), self._theme.get_option('height'))
			cr.fill()

		# add plugin image
		if not image:
			image = os.path.join(UI_DIR, 'mumbles.png')
		plugin_image = gtk.gdk.pixbuf_new_from_file_at_size(image, self._theme.get_option('icon/width'), self._theme.get_option('icon/height'))
		if plugin_image:
			widget.window.draw_pixbuf(None, plugin_image, 0, 0, self._theme.get_option('icon/xpos'), self._theme.get_option('icon/ypos'))

		cr.reset_clip()

		# add the title
		text_title_width = self._theme.get_option('text/title/width')
		text_title_height = self._theme.get_option('text/title/height')
		text_title_padding_left = self._theme.get_option('text/title/padding/left')
		text_title_padding_right = self._theme.get_option('text/title/padding/right')
		text_title_padding_upper = self._theme.get_option('text/title/padding/upper')
		text_title_padding_lower = self._theme.get_option('text/title/padding/lower')

		left_edge = (0 + text_title_padding_left)
		upper_edge = (0 + text_title_padding_upper)
		right_edge = (text_title_width - text_title_padding_right)
		lower_edge = (text_title_height - text_title_padding_lower)

		p_layout_title = cr.create_layout()
		p_layout_title.set_wrap(pango.WRAP_CHAR)
		p_layout_title.set_width((right_edge - left_edge) * pango.SCALE)

		p_fdesc = pango.FontDescription()
		p_fdesc.set_family_static(self._theme.get_option('text/title/font/family'))
		p_fdesc.set_size(self._theme.get_option('text/title/font/size') * pango.SCALE)
		p_fdesc.set_weight(pango.WEIGHT_BOLD)

		p_layout_title.set_font_description(p_fdesc)
		p_layout_title.set_text(title)

		cr.rectangle(0, 0, right_edge, (upper_edge + lower_edge))
		cr.clip()
		cr.move_to(left_edge, upper_edge)

		c = gtk.gdk.color_parse(self._theme.get_option('text/title/font/color'))
		cr.set_source_color(c)
		cr.show_layout(p_layout_title)

		cr.reset_clip()

		# add the message
		text_message_width = self._theme.get_option('text/message/width')
		text_message_height = self._theme.get_option('text/message/height')
		text_message_padding_left = self._theme.get_option('text/message/padding/left')
		text_message_padding_right = self._theme.get_option('text/message/padding/right')
		text_message_padding_upper = self._theme.get_option('text/message/padding/upper')
		text_message_padding_lower = self._theme.get_option('text/message/padding/lower')

		left_edge = (0 + text_message_padding_left)
		upper_edge = (text_message_padding_upper + text_title_height) # here start the top edge at the bottom of the title
		right_edge = (text_message_width - text_message_padding_right)
		lower_edge = (text_message_height - text_message_padding_lower)

		p_layout_message = cr.create_layout()
		p_layout_message.set_wrap(pango.WRAP_WORD)
		p_layout_message.set_width((right_edge - left_edge) * pango.SCALE)

		p_fdesc = pango.FontDescription()
		p_fdesc.set_family(self._theme.get_option('text/message/font/family'))
		p_fdesc.set_size(self._theme.get_option('text/message/font/size') * pango.SCALE)
		p_fdesc.set_weight(pango.WEIGHT_BOLD)

		p_layout_message.set_font_description(p_fdesc)
		p_layout_message.set_text(message)

		cr.rectangle(0, 0, right_edge, (upper_edge + lower_edge))
		cr.clip()
		cr.move_to(left_edge, upper_edge)

		cr.set_source_rgba(1, 1, 1)
		cr.show_layout(p_layout_message)

		c = gtk.gdk.color_parse(self._theme.get_option('text/message/font/color'))
		cr.set_source_color(c)
		cr.show_layout(p_layout_message)

		return False

	def screen_changed(self, widget, old_screen=None):
        
		# To check if the display supports alpha channels, get the colormap
		screen = widget.get_screen()
		try:
			colormap = screen.get_rgba_colormap()
			self._alpha_available = True
		except:
			colormap = None

		if colormap == None:
			self._alpha_available = False
			try:
				colormap = screen.get_rgb_colormap()
				self._alpha_available = False
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
				self._n_active -= 1
			win.window.destroy()
		except:
			# decrease number of active windows
			self._n_active -= 1
			win.hide()

		# if number of active windows is back to 0, reset starting point
		if self._n_active == 0:
			self._n_index = 0

	def alert(self, alert_object):
		plugin_name = alert_object.get_name()
		name = alert_object.get_title()
		message = alert_object.get_msg()
		image = alert_object.get_icon()

		# setup window
		win = gtk.Window(gtk.WINDOW_TOPLEVEL)

		win.set_title('Mumbles')
		win.add_events(gtk.gdk.BUTTON_PRESS_MASK)

		win.connect('delete-event', gtk.main_quit)
		win.connect('expose-event', self.expose, name, message, image)
		win.connect('screen-changed', self.screen_changed)

		try:
			win.connect('button-press-event', self._click_handlers[plugin_name], plugin_name)
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
		win.resize( self._theme.get_option('width'),
			self._theme.get_option('height'))

		# adjust window position by direction and placement
		# preferences and how many notifications are active
		spacing = self._theme.get_option('spacing')

		notify_height = self._theme.get_option('height')

		try:
			cur_direction =  self.get_option('direction')
		except:
			print "Warning: Invalid value of %s for notification_direction. Falling back to default value." %(self.get_option('direction'))
			cur_direction = CONFIG_NOTIFY_DIRECTION_DOWN

		if cur_direction == CONFIG_NOTIFY_DIRECTION_DOWN:

			if self._n_index == 0:
				new_y = PANEL_HEIGHT
			else:
				new_y = self._current_y + notify_height + spacing

		else:
			if self._n_index == 0:
				new_y = gtk.gdk.screen_height() - notify_height - PANEL_HEIGHT
			else:
				new_y = self._current_y - notify_height - spacing

		self._current_y = new_y

		try:
			cur_placement = self.get_option('placement')
		except:
			print "Warning: Invalid value of %s for notification_placement. Falling back to default value." %(self.get_option('placement'))
			cur_placement = CONFIG_NOTIFY_PLACEMENT_RIGHT
		if cur_placement == CONFIG_NOTIFY_PLACEMENT_RIGHT:
			new_x = (gtk.gdk.screen_width()-self._theme.get_option('width')-spacing)
		else:
			new_x = spacing 
		win.move(new_x, new_y)

		# increase number of active notifications
		self._n_index += 1
		self._n_active += 1

		# show window for a defined about of time
		try:
			cur_duration = self.get_option('duration')
		except:
			print "Warning: Invalid value of %s for notification_duration. Falling back to default value." %(self.get_option('duration'))
			cur_duration = 5
		source_id = gobject.timeout_add(cur_duration*1000, self.close_alert, win)

		# finally show (and trigger the expose event)
		win.show_all()

		return True
