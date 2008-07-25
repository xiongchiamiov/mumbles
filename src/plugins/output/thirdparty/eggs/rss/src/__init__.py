#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# RSS Mumbles Output Plugin
#
#------------------------------------------------------------------------

from MumblesOutputPlugin import *
from xml.dom import minidom
from xml.sax.saxutils import escape
import rfc822
from os import path

DEFAULT_FEED_TITLE = 'mumbles'
DEFAULT_FEED_LINK = 'http://mumbles-project.org'
DEFAULT_FEED_DESCRIPTION = 'rss feed of mumbles notifications'
DEFAULT_FEED_LOCATION = path.expanduser('~/.mumbles/mumbles_rss.xml')
DEFAULT_FEED_MAX_ITEMS = 10

class RSSMumblesOutput(MumblesOutputPlugin):

	plugin_name = "RSSMumblesOutput"

	def __init__(self, session_bus, options=None, verbose=False):
		MumblesOutputPlugin.__init__(self, session_bus, options, verbose)

	def init_options(self):
		self.add_option(TextOption('title',
			DEFAULT_FEED_TITLE,
			'Title',
			'The RSS feed title.'))

		self.add_option(TextOption('link',
			DEFAULT_FEED_LINK,
			'Link',
			'The RSS feed link.'))

		self.add_option(TextOption('description',
			DEFAULT_FEED_DESCRIPTION,
			'Description',
			'The RSS feed description.'))

		self.add_option(TextOption('location',
			DEFAULT_FEED_LOCATION,
			'Location',
			'The location of the rss file.'))

		self.add_option(IntegerOption('maxitems',
			DEFAULT_FEED_MAX_ITEMS,
			'Max Number of Items',
			'The maximum number of items to show in the feed.'))

	def alert(self, alert_object):
		feed_title = self.get_option('title')
		feed_link = self.get_option('link')
		feed_description = self.get_option('description')
		feed_location = self.get_option('location')
		feed_maxitems = self.get_option('maxitems')

		items = []
		if path.exists(feed_location):
			dom = minidom.parse(feed_location)
			for item in dom.getElementsByTagName('item'):
					items.append({
						'title': self._get_node_text(item.getElementsByTagName('title')[0].childNodes),
						#'link': self._get_node_text(item.getElementsByTagName('link')[0].childNodes),
						'description': self._get_node_text(item.getElementsByTagName('description')[0].childNodes)
					})

		while (len(items) + 1) > feed_maxitems:
			items.pop()

		items.insert(0, {
				'title': alert_object.get_title(),
				#'link': '',
				'description': alert_object.get_msg()
		})

		t = rfc822.formatdate()

		r = "<?xml version=\"1.0\"?>\n"
		r += "<rss version=\"0.92\">\n"
		r += "\t<channel>\n"
		r += "\t\t<title>"+feed_title+"</title>\n"
		r += "\t\t<link>"+feed_link+"</link>\n"
		r += "\t\t<description>"+feed_description+"</description>\n"
		r += "\t\t<lastBuildDate>"+t+"</lastBuildDate>\n"

		for i in items:
			r += "\t\t<item>\n"
			r += "\t\t\t<title>"+escape(i['title'])+"</title>\n"
			#r += "\t\t\t<link>"+i['link']+"</link>\n"
			r += "\t\t\t<description>"+escape(i['description'])+"</description>\n"
			r += "\t\t</item>\n"
		
		r += "\t</channel>\n"
		r += "</rss>\n"

		f = open(feed_location, 'w+')
		f.write(r)
		f.close

	def _get_node_text(self, nodelist):
		t = ""
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				t = t + node.data
		return t 

