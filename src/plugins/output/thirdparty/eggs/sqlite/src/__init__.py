#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# SQLite Mumbles Output Plugin
#
#------------------------------------------------------------------------

from MumblesOutputPlugin import *
from os import path
from pysqlite2 import dbapi2 as sqlite

DEFAULT_DB_LOCATION = path.expanduser('~/.mumbles/mumbles_sqlite.db')
MUMBLES_ICON = path.join(UI_DIR, 'mumbles.png')

class SQLiteMumblesOutput(MumblesOutputPlugin):

	plugin_name = "SQLiteMumblesOutput"

	def __init__(self, session_bus, options=None, verbose=False):
		MumblesOutputPlugin.__init__(self, session_bus, options, verbose)

		self.sql = {
			'table_name': 'history',
			'insert': 'INSERT INTO history (icon, title, msg) VALUES (?, ?, ?)'
		}
		try:
			self.connect()
		except Exception, e:
			print "Error: %s" %e

	def init_options(self):
		self.add_option(TextOption('location',
			DEFAULT_DB_LOCATION,
			'sqlite file',
			'The location of the database file'))

	def get_name(self):
		return self.plugin_name

	def alert(self, alert_object):
		icon = alert_object.get_icon()
		if not icon:
			icon = MUMBLES_ICON
		insert = (icon, alert_object.get_title(), alert_object.get_msg())
		try:
			self.cursor.execute(self.sql['insert'], insert)
			self.connection.commit()
		except Exception, e:
			print "Error: %s" %e

	def connect(self):
		self.connection = sqlite.connect(self.get_option('location'))
		self.cursor = self.connection.cursor()

