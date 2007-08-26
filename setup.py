#!/usr/bin/env python

from distutils.core import setup
import os
import glob

dist = setup(name='mumbles',
	version='0.4',
	author='dot_j',
	author_email='dot_j@mumbles-project.org',
	maintainer='dot_j',
	maintainer_email='dot_j@mumbles-project.org',
	description='Mumbles is notification system for the Gnome desktop.',
	long_description='Mumbles is a plugin-driven, DBus based notification system written for the Gnome desktop. Similar to libnotify notifications and Growl for OSX (http://growl.info), Mumbles aims to provide a modern notification system for the GNU/Linux Desktop.',
	url='http://www.mumbles-project.org/',
	download_url='http://www.mumbles-project.org/download',
	license='GNU GPL',
	platforms='linux',
	scripts=['bin/mumbles'],
	packages=['src'],
	data_files=[
		('share/mumbles/', glob.glob("src/ui/*.glade")),
		('share/mumbles/', ["src/ui/mumbles.png"]),
		('share/icons/hicolor/22x22/apps', ['images/mumbles.png']),
		('share/icons/hicolor/scalable/apps', ['src/ui/mumbles.svg']),
		('share/pixmaps', ['src/ui/mumbles.png']),
		('share/applications', ['bin/mumbles.desktop']),
		('share/mumbles/plugins', glob.glob("src/plugins/*.egg"))
		]
)
