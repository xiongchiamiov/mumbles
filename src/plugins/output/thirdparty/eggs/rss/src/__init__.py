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

FEED_TITLE = 'mumbles'
FEED_LINK = 'http://mumbles-project.org'
FEED_DESCRIPTION = 'rss feed of mumbles notifications'
FEED_LOCATION = path.expanduser('~/.mumbles/mumbles_rss.xml')
FEED_MAX_ITEMS = 10

class RSSMumblesOutput(MumblesOutputPlugin):

	plugin_name = "RSSMumblesOutput"

	def __init__(self, session_bus, options=None, verbose=False):
		MumblesOutputPlugin.__init__(self, session_bus, options, verbose)

	def get_name(self):
		return self.plugin_name

	def alert(self, alert_object):

		items = []
		if path.exists(FEED_LOCATION):
			dom = minidom.parse(FEED_LOCATION)
			for item in dom.getElementsByTagName('item'):
					items.append({
						'title': self._get_node_text(item.getElementsByTagName('title')[0].childNodes),
						#'link': self._get_node_text(item.getElementsByTagName('link')[0].childNodes),
						'description': self._get_node_text(item.getElementsByTagName('description')[0].childNodes)
					})

		while (len(items) + 1) > FEED_MAX_ITEMS:
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
		r += "\t\t<title>"+FEED_TITLE+"</title>\n"
		r += "\t\t<link>"+FEED_LINK+"</link>\n"
		r += "\t\t<description>"+FEED_DESCRIPTION+"</description>\n"
		r += "\t\t<lastBuildDate>"+t+"</lastBuildDate>\n"

		for i in items:
			r += "\t\t<item>\n"
			r += "\t\t\t<title>"+escape(i['title'])+"</title>\n"
			#r += "\t\t\t<link>"+i['link']+"</link>\n"
			r += "\t\t\t<description>"+escape(i['description'])+"</description>\n"
			r += "\t\t</item>\n"
		
		r += "\t</channel>\n"
		r += "</rss>\n"

		f = open(FEED_LOCATION, 'w+')
		f.write(r)
		f.close

	def _get_node_text(self, nodelist):
		t = ""
		for node in nodelist:
			if node.nodeType == node.TEXT_NODE:
				t = t + node.data
		return t 

