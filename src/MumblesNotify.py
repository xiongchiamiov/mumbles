#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Notifier
#
#------------------------------------------------------------------------

import pango
import cairo

import gobject

import gtk
import pygtk
pygtk.require('2.0')

from MumblesGlobals import *
from OptionsHandler import *

class MumblesNotifyOptions(OptionsHandler):

	def __init__(self):
		OptionsHandler.__init__(self)

		self.options['mumbles-notifications'] = {

			# dimenstions of the notification area
			'width' : 250,
			'height' : 80,

			# theme directory
			'theme' : 'default',

			# icon options
			'icon_x_pos' : 10,
			'icon_y_pos' : 25,

			# text formatting
			'text_font' : 'Sans',
			'text_title_color' : '#fff',
			'text_title_size' : 10,
			'text_message_color' : '#fff',
			'text_message_size' : 8,
			'text_x_pos' : 38,
			'text_y_pos' : 8,
			'text_x_padding' : 15,
			'text_y_padding' : 15
		}



class MumblesNotify(object):

	def __init__(self, options = None):

		# get default notification options
		self.options = MumblesNotifyOptions()

		if options:
			self.options.add_options(options)

		# keep track of how many notices deep we are
		self.__n_index = 0

		# keep track of how many active notices there are
		self.__n_active = 0

		# spacing between notifications
		# (to-do: window placement currently calculated assuming this is 10)
		self.__spacing = 10

		self.__click_handlers = {}

	def addClickHandler(self, plugin_name, click_handler):
		self.__click_handlers[plugin_name] = click_handler

	def clicked(self, widget, event, plugin_name = None):
		try:
			self.__click_handlers[plugin_name](widget, event, plugin_name)
		except:
			if event.button == 3:
				self.close(widget.window);

	def expose(self, widget, event, name, message, image):

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
		background_image = os.path.join(THEMES_DIR, self.options.get_option('mumbles-notifications', 'theme'), 'bground.png')
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
			cr.rectangle(0, 0, self.options.get_option('mumbles-notifications', 'width'), self.options.get_option('mumbles-notifications', 'height'))
			cr.fill()


		# add plugin image
		plugin_image_width = 0
		if not image:
			image = os.path.join(UI_DIR, 'mumbles.png')
		plugin_image = gtk.gdk.pixbuf_new_from_file(image)
		if plugin_image:
			plugin_image_width = plugin_image.get_width()
			widget.window.draw_pixbuf(None, plugin_image, 0, 0, self.options.get_option('mumbles-notifications', 'icon_x_pos'), self.options.get_option('mumbles-notifications', 'icon_y_pos'))


		# add text
		cr.rectangle(0, 0, self.options.get_option('mumbles-notifications', 'width'), self.options.get_option('mumbles-notifications', 'height') - self.options.get_option('mumbles-notifications', 'text_y_padding'))
		cr.clip()
		cr.translate(self.options.get_option('mumbles-notifications', 'text_x_pos'), self.options.get_option('mumbles-notifications', 'text_y_pos'))

		p_layout = cr.create_layout()
		p_layout.set_wrap(pango.WRAP_WORD)
		p_layout.set_width((self.options.get_option('mumbles-notifications', 'width') - plugin_image_width - self.options.get_option('mumbles-notifications', 'text_x_padding')) * pango.SCALE)

		title = '<span foreground="'+self.options.get_option('mumbles-notifications', 'text_title_color')+'" font_desc="'+self.options.get_option('mumbles-notifications', 'text_font')+' '+`self.options.get_option('mumbles-notifications', 'text_title_size')`+'"><b>'+name+'</b></span>\n'

		message = '<span foreground="'+self.options.get_option('mumbles-notifications', 'text_message_color')+'" font_desc="'+self.options.get_option('mumbles-notifications', 'text_font')+' '+`self.options.get_option('mumbles-notifications', 'text_message_size')`+'"><b>'+message+'</b></span>'

		p_layout.set_markup(title+message)

		cr.show_layout(p_layout)
		cr.fill()

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
		win.resize( self.options.get_option('mumbles-notifications', 'width'),
			self.options.get_option('mumbles-notifications', 'height'))

		# adjust window position by direction and placement
		# preferences and how many notifications are active
		if int(self.options.get_option('mumbles-notifications', 'notification_direction')) == NOTIFY_DIRECTION_DOWN:
			new_y = ((self.options.get_option('mumbles-notifications', 'height')*(self.__n_index)) + self.__spacing )+ (self.__spacing*(self.__n_index+1))
		else:
			new_y = gtk.gdk.screen_height() - ((self.options.get_option('mumbles-noifications', 'height')*(self.__n_index+1) + self.__spacing) + (self.__spacing*(self.__n_index+2)))

		if int(self.options.get_option('mumbles-notifications','notification_placement')) == NOTIFY_PLACEMENT_RIGHT:
			new_x = (gtk.gdk.screen_width()-self.options.get_option('mumbles-notifications', 'width')-self.__spacing)
		else:
			new_x = self.__spacing 
		win.move(new_x, new_y)

		# increase number of active notifications
		self.__n_index += 1
		self.__n_active += 1

		# show window for a defined about of time
		source_id = gobject.timeout_add(int(self.options.get_option('mumbles-notifications', 'notification_duration'))*1000, self.close_alert, win)

		# finally show (and trigger the expose event)
		win.show_all()

		return True
