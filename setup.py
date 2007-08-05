#!/usr/bin/env python
#
# THIS FILE IS PART OF THE MUMBLES PROJECT AND IS LICENSED UNDER THE GPL.
# SEE THE 'COPYING' FILE FOR DETAILS
#
# Mumbles Setup Script
#
#------------------------------------------------------------------------

try:
        import pkg_resources
except:
        print "It appears that you do not have setuptools installed.\nPlease install python setuptools before installing mumbles"
        raise SystemExit

import os

# build develop egg links for the 3 default plugins
os.system('cd ./src/plugins/generic; python setup.py develop --install-dir .. -m')
os.system('cd ./src/plugins/gaim; python setup.py develop --install-dir .. -m')
os.system('cd ./src/plugins/pidgin; python setup.py develop --install-dir .. -m')
os.system('cd ./src/plugins/rhythmbox; python setup.py develop --install-dir .. -m')
os.system('cd ./src/plugins/firefox; python setup.py develop --install-dir .. -m')
os.system('cd ./src/plugins/thunderbird; python setup.py develop --install-dir .. -m')

print "\nInstallation Complete. You can now run mumbles by typing ./mumbles\n"
