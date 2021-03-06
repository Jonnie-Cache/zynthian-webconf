# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# Display Configuration Handler
#
# Copyright (C) 2017 Fernando Moyano <jofemodo@zynthian.org>
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
import logging
import tornado.web
from subprocess import check_output
from collections import OrderedDict
from lib.zynthian_config_handler import ZynthianConfigHandler

#------------------------------------------------------------------------------
# Display Configuration
#------------------------------------------------------------------------------

class DisplayConfigHandler(ZynthianConfigHandler):

	display_presets=OrderedDict([
		['PiTFT 2.8 Resistive', {
			'DISPLAY_CONFIG': 'dtoverlay=pitft28-resistive,rotate=90,speed=32000000,fps=20',
			'DISPLAY_WIDTH': '320',
			'DISPLAY_HEIGHT': '240',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['PiTFT 2.8 Capacitive', {
			'DISPLAY_CONFIG': 'dtoverlay=pitft28-capacitive,rotate=90,speed=32000000,fps=20',
			'DISPLAY_WIDTH': '320',
			'DISPLAY_HEIGHT': '240',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['PiTFT 3.5 Resistive', {
			'DISPLAY_CONFIG': 'dtoverlay=pitft35-resistive,rotate=90,speed=32000000,fps=20',
			'DISPLAY_WIDTH': '480',
			'DISPLAY_HEIGHT': '320',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['PiScreen 3.5 (v1)', {
			'DISPLAY_CONFIG': 'dtoverlay=piscreen,speed=16000000,rotate=90',
			'DISPLAY_WIDTH': '480',
			'DISPLAY_HEIGHT': '320',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['PiScreen 3.5 (v2)', {
			'DISPLAY_CONFIG': 'dtoverlay=piscreen2r-notouch,rotate=270\n'+
				'dtoverlay=ads7846,speed=2000000,cs=1,penirq=17,penirq_pull=2,swapxy=1,xohms=100,pmax=255',
			'DISPLAY_WIDTH': '480',
			'DISPLAY_HEIGHT': '320',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['RPi-Display 2.8', {
			'DISPLAY_CONFIG': 'dtoverlay=rpi-display,speed=32000000,rotate=270',
			'DISPLAY_WIDTH': '320',
			'DISPLAY_HEIGHT': '240',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 3.2B', {
			'DISPLAY_CONFIG': 'dtoverlay=waveshare32b:rotate=270,swapxy=1\n'+
				'#dtoverlay=ads7846,cs=1,penirq_pull=2,speed=1000000,keep_vref_on=1,swapxy=0,pmax=255,xohms=60,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 3.5A', {
			'DISPLAY_CONFIG': 'dtoverlay=waveshare35a\n'+
				'dtoverlay=ads7846,cs=1,penirq_pull=2,speed=1000000,keep_vref_on=1,swapxy=1,pmax=255,xohms=60,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 3.5B', {
			'DISPLAY_CONFIG': 'dtoverlay=waveshare35b\n'+
				'dtoverlay=ads7846,cs=1,penirq_pull=2,speed=1000000,keep_vref_on=1,swapxy=1,pmax=255,xohms=60,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 3.5C', {
			'DISPLAY_CONFIG': 'dtoverlay=waveshare35c\n'+
				'dtoverlay=ads7846,cs=1,penirq_pull=2,speed=1000000,keep_vref_on=1,swapxy=1,pmax=255,xohms=60,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 4 GPIO-only', {
			'DISPLAY_CONFIG': 'dtoverlay=waveshare35a:rotate=90\n'+
				'dtoverlay=ads7846,cs=1,penirq_pull=2,speed=1000000,keep_vref_on=1,swapxy=0,pmax=255,xohms=60,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb1'
		}],
		['WaveShare 4 HDMI/GPIO', {
			'DISPLAY_CONFIG': 'hdmi_drive=1\n'+
				'hdmi_group=2\n'+
				'hdmi_mode=1\n'+
				'hdmi_mode=87\n'+
				'hdmi_cvt 800 480 60 6 0 0 0\n'+
				'dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '800',
			'DISPLAY_HEIGHT': '480',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['WaveShare 5 HDMI/GPIO', {
			'DISPLAY_CONFIG': 'hdmi_drive=1\n'+
				'hdmi_group=2\n'+
				'hdmi_mode=1\n'+
				'hdmi_mode=87\n'+
				'hdmi_cvt 800 480 60 6 0 0 0\n'+
				'dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '800',
			'DISPLAY_HEIGHT': '480',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['WaveShare 5 HDMI/USB', {
			'DISPLAY_CONFIG': 'hdmi_drive=1\n'+
				'hdmi_group=2\n'+
				'hdmi_mode=1\n'+
				'hdmi_mode=87\n'+
				'hdmi_cvt 800 480 60 6 0 0 0',
			'DISPLAY_WIDTH': '800',
			'DISPLAY_HEIGHT': '480',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['WaveShare 7 HDMI/GPIO', {
			'DISPLAY_CONFIG': 'hdmi_drive=1\n'+
				'hdmi_group=2\n'+
				'hdmi_mode=1\n'+
				'hdmi_mode=87\n'+
				'hdmi_cvt 1024 600 60 6 0 0 0\n'+
				'dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900',
			'DISPLAY_WIDTH': '1024',
			'DISPLAY_HEIGHT': '600',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['WaveShare 7 HDMI/USB', {
			'DISPLAY_CONFIG': 'hdmi_drive=1\n'+
				'hdmi_group=2\n'+
				'hdmi_mode=1\n'+
				'hdmi_mode=87\n'+
				'hdmi_cvt 1024 600 60 6 0 0 0',
			'DISPLAY_WIDTH': '1024',
			'DISPLAY_HEIGHT': '600',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['Generic HDMI display', {
			'DISPLAY_CONFIG': 'disable_overscan=1\n',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': '/dev/fb0'
		}],
		['Custom device', {
			'DISPLAY_CONFIG': '',
			'DISPLAY_WIDTH': '',
			'DISPLAY_HEIGHT': '',
			'FRAMEBUFFER': ''
		}]
	])

	@tornado.web.authenticated
	def get(self, errors=None):
		config=OrderedDict([
			['DISPLAY_NAME', {
				'type': 'select',
				'title': 'Display',
				'value': os.environ.get('DISPLAY_NAME'),
				'options': list(self.display_presets.keys()),
				'presets': self.display_presets
			}],
			['DISPLAY_CONFIG', {
				'type': 'textarea',
				'rows': 4,
				'cols': 50,
				'title': 'Config',
				'value': os.environ.get('DISPLAY_CONFIG'),
				'advanced': True
			}],
			['DISPLAY_WIDTH', {
				'type': 'text',
				'title': 'Width',
				'value': os.environ.get('DISPLAY_WIDTH'),
				'advanced': True
			}],
			['DISPLAY_HEIGHT', {
				'type': 'text',
				'title': 'Height',
				'value': os.environ.get('DISPLAY_HEIGHT'),
				'advanced': True
			}],
			['FRAMEBUFFER', {
				'type': 'text',
				'title': 'Frambuffer',
				'value': os.environ.get('FRAMEBUFFER'),
				'advanced': True
			}]
		])
		if self.genjson:
			self.write(config)
		else:
			self.render("config.html", body="config_block.html", config=config, title="Display", errors=errors)

	@tornado.web.authenticated
	def post(self):
		errors=self.update_config(tornado.escape.recursive_unicode(self.request.arguments))
		self.delete_fb_splash() # New splash-screens will be generated on next boot
		#self.restart_ui()
		self.redirect('/api/sys-reboot')
		self.get(errors)

	def delete_fb_splash(self):
		try:
			cmd="rm -rf %s/img" % os.environ.get('ZYNTHIAN_CONFIG_DIR')
			check_output(cmd, shell=True)
		except Exception as e:
			logging.error("Deleting FrameBuffer Splash Screens: %s" % e)

	def needs_reboot(self):
		return True
