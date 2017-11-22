#!/usr/bin/python3
# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# Web Service API
#
# Copyright (C) 2015-2017 Fernando Moyano <jofemodo@zynthian.org>
#
#********************************************************************
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
#
#********************************************************************

import os
import re
import sys
import logging
import tornado.ioloop
import tornado.web
from collections import OrderedDict
from lib.LoginHandler import LoginHandler
from lib.AudioConfigHandler import AudioConfigHandler
from lib.DisplayConfigHandler import DisplayConfigHandler
from lib.RebootHandler import RebootHandler
from lib.SecurityConfigHandler import SecurityConfigHandler
from lib.UiConfigHandler import UiConfigHandler
from lib.WiringConfigHandler import WiringConfigHandler
from lib.WifiConfigHandler import WifiConfigHandler
from lib.WifiListHandler import WifiListHandler
from lib.SnapshotConfigHandler import SnapshotConfigHandler
from lib.MidiConfigHandler import MidiConfigHandler
from lib.soundfont_config_handler import SoundfontConfigHandler
from lib.upload_handler import UploadHandler, UploadPollingHandler
from lib.SystemBackupHandler import SystemBackupHandler
from lib.system_update_handler import SystemUpdateHandler, UpdateLogHandler
from lib.presets_config_handler import PresetsConfigHandler

#------------------------------------------------------------------------------

#Configure Logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#------------------------------------------------------------------------------
# Build Web App & Start Server
#------------------------------------------------------------------------------

def make_app():
	settings = {
		"template_path": "templates",
		"cookie_secret": "hsa9fKjf3Hf923hg6avJ)8fjh3mcGF12ht97834bh",
		"login_url": "/login",
		"upload_progress_handler": dict()
	}
	return tornado.web.Application([
		(r'/$', AudioConfigHandler),
		#(r'/()$', tornado.web.StaticFileHandler, {'path': 'html', "default_filename": "index.html"}),
		(r'/(.*\.html)$', tornado.web.StaticFileHandler, {'path': 'html'}),
		(r'/(favicon\.ico)$', tornado.web.StaticFileHandler, {'path': 'img'}),
		(r'/img/(.*)$', tornado.web.StaticFileHandler, {'path': 'img'}),
		(r'/css/(.*)$', tornado.web.StaticFileHandler, {'path': 'css'}),
		(r'/js/(.*)$', tornado.web.StaticFileHandler, {'path': 'js'}),
		(r'/bower_components/(.*)$', tornado.web.StaticFileHandler, {'path': 'bower_components'}),
		(r"/login", LoginHandler),
		(r"/api/lib-snapshot$", SnapshotConfigHandler),
		(r"/api/lib-soundfont$", SoundfontConfigHandler),
		(r"/api/upload$", UploadHandler),
		(r"/api/upload-polling$", UploadPollingHandler),
		(r"/api/lib-presets$", PresetsConfigHandler),
		(r"/api/hw-audio$", AudioConfigHandler),
		(r"/api/hw-display$", DisplayConfigHandler),
		(r"/api/hw-wiring$", WiringConfigHandler),
		(r"/api/ui-style$", UiConfigHandler),
		(r"/api/ui-midi$", MidiConfigHandler),
		(r"/api/sys-wifi$", WifiConfigHandler),
		(r"/api/sys-backup$", SystemBackupHandler),
		(r"/api/sys-update$", SystemUpdateHandler),
		(r"/api/sys-update-log$", UpdateLogHandler),
		(r"/api/sys-security$", SecurityConfigHandler),
		(r"/api/sys-reboot$", RebootHandler),
		(r"/api/wifi/list$", WifiListHandler),
	], **settings)

if __name__ == "__main__":
	app = make_app()
	app.listen(80, max_body_size=6*1024*1024*1024)
	tornado.ioloop.IOLoop.current().start()

#------------------------------------------------------------------------------
