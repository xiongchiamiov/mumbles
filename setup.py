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

print "\nInstallation Complete. You can now run mumbles by typing ./mumbles\n"
