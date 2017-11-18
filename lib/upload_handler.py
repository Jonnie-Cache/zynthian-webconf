# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# SoundFont Manager Handler
#
# Copyright (C) 2017 Markus Heidt <markus@heidt-tech.com>
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
import sys
import logging
import tornado.web
import shutil

from lib.post_streamer import PostDataStreamer

#------------------------------------------------------------------------------
# Soundfont Configuration
#------------------------------------------------------------------------------



class UploadPostDataStreamer(PostDataStreamer):
    percent = 0

    def on_progress(self):
        """Override this function to handle progress of receiving data."""
        if self.total:
            new_percent = self.received*100//self.total
            if new_percent != self.percent:
                self.percent = new_percent
                logging.info("upload progress: " + str(new_percent))


@tornado.web.stream_request_body
class UploadHandler(tornado.web.RequestHandler):

	def get_current_user(self):
		return self.get_secure_cookie("user")

	@tornado.web.authenticated
	def get(self, errors=None):
		self.write('''<html><body>No GET supported</body></html>''')

	def post(self):
		try:
			#self.fout.close()
			self.ps.finish_receive()
			# Use parts here!
			redirectUrl = "#"
			try:
				destinationPath = self.get_argument("destinationPath")
				redirectUrl = self.get_argument("redirectUrl")
				for part in self.ps.parts:
					sourceFilename = part["tmpfile"].name
					destinationFilename = self.ps.get_part_ct_param(part, "filename", None)
					if destinationFilename:
						destinationFullPath = destinationPath + "/" + destinationFilename
						redirectUrl += "?ZYNTHIAN_UPLOAD_NEW_FILE=" + destinationFullPath
						logging.info("copy " + sourceFilename + " to " + destinationFullPath  )
						shutil.move(sourceFilename, destinationFullPath)
			except:
				pass

			self.redirect(redirectUrl)
		finally:
			# Don't forget to release temporary files.
			self.ps.release_parts()

	def prepare(self):
		try:
			total = int(self.request.headers.get("Content-Length","0"))
		except:
			total = 0
		self.ps = UploadPostDataStreamer(total) #,tmpdir="/tmp"
		#self.fout = open("raw_received.dat","wb+")

	def data_received(self, chunk):
		#self.fout.write(chunk)
		self.ps.receive(chunk)
