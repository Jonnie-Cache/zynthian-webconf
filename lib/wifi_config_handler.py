# -*- coding: utf-8 -*-
#********************************************************************
# ZYNTHIAN PROJECT: Zynthian Web Configurator
#
# WIFI Configuration Handler
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
import re
import logging
import base64
import tornado.web
import subprocess
from collections import OrderedDict


#------------------------------------------------------------------------------
# Wifi Config Handler
#------------------------------------------------------------------------------

class WifiConfigHandler(tornado.web.RequestHandler):


	PASSWORD_MASK = "*****"
	WPA_FIELD_MAP = { "ZYNTHIAN_WIFI_PRIORITY": "priority" }
	HOSTAPD_FILE = "/etc/hostapd/hostapd.conf"
	HOSTAPD_SSID = "ssid"
	HOSTAPD_PWD = "wpa_passphrase"
	HOSTAPD_SERVICE_ACTIVITY_CHANGED = "servicve_activity_changed"
	HOSTAPD_SERVICE = "autohotspot"


	def get_current_user(self):
		return self.get_secure_cookie("user")


	def prepare(self):
		self.genjson=False
		try:
			if self.get_query_argument("json"):
				self.genjson=True
		except:
			pass


	@tornado.web.authenticated
	def get(self, errors=None):
		hostapd_parameters = self.get_hostapd_parameters()
		self.do_get(hostapd_parameters, errors)

	@tornado.web.authenticated
	def do_get(self, hostapd_parameters, errors=None):

		supplicant_file_name = self.get_supplicant_file_name()
		supplicant_data = re.sub(r'psk=".*?"', 'psk="' + WifiConfigHandler.PASSWORD_MASK + '"',
			self.read_supplicant_data(supplicant_file_name),
			re.I | re.M | re.S )
		p = re.compile('.*?network=\\{.*?ssid=\\"(.*?)\\".*?psk=\\"(.*?)\\".*?priority=(\d*).*?\\}.*?', re.I | re.M | re.S )
		iterator = p.finditer(supplicant_data)
		config=OrderedDict([
			['ZYNTHIAN_WIFI_WPA_SUPPLICANT', {
				'type': 'textarea',
				'cols': 50,
				'rows': 20,
				'title': 'Advanced Config',
				'value': supplicant_data
			}],
			['ZYNTHIAN_WIFI_HOSTAPD_EXISTS', len(hostapd_parameters)>0],
			['ZYNTHIAN_WIFI_HOSTAPD_ACTIVE', {
				'type': 'checkbox',
				'title': 'Active',
				'value': self.is_hostapd_active()
			}],
			['ZYNTHIAN_WIFI_HOSTAPD_NAME', {
				'type': 'text',
				'title': 'Hotspot name',
				'value':  hostapd_parameters[self.HOSTAPD_SSID] if self.HOSTAPD_SSID in hostapd_parameters else ''
			}],
			['ZYNTHIAN_WIFI_HOSTAPD_PASSWORD', {
				'type': 'password',
				'title': 'Password'
			}]

		])

		networks = []
		idx = 0
		for m in iterator:
			networks.append({
			    'idx': idx,
				'ssid': m.group(1),
				'ssid64': base64.b64encode(m.group(1).encode())[:5],
				'psk': m.group(2),
				'priority': m.group(3)
			})
			idx+=1

		config['ZYNTHIAN_WIFI_NETWORKS'] = networks

		config[self.HOSTAPD_SERVICE_ACTIVITY_CHANGED] = hostapd_parameters[self.HOSTAPD_SERVICE_ACTIVITY_CHANGED] if self.HOSTAPD_SERVICE_ACTIVITY_CHANGED in hostapd_parameters else False

		if self.genjson:
			self.write(config)
		else:
			self.render("config.html", body="wifi.html", config=config, title="Wifi", errors=errors)


	@tornado.web.authenticated
	def post(self):
		hostapd_parameters = self.get_hostapd_parameters()

		self.post_hostapd(hostapd_parameters)


		wpa_supplicant_data = self.get_argument('ZYNTHIAN_WIFI_WPA_SUPPLICANT')
		fieldNames = ["ZYNTHIAN_WIFI_PRIORITY"]
		wpa_supplicant_data = self.apply_updated_fields(wpa_supplicant_data, fieldNames)

		newSSID =  self.get_argument('ZYNTHIAN_WIFI_NEW_SSID')
		if newSSID: wpa_supplicant_data = self.add_new_network(wpa_supplicant_data, newSSID)

		fo = open("/etc/wpa_supplicant/wpa_supplicant.conf", "w")
		fo.write(wpa_supplicant_data)
		fo.flush()
		fo.close()

		errors=self.do_get(hostapd_parameters)

	def post_hostapd(self, hostapd_parameters):
		if len(hostapd_parameters)>0:
			has_new_name = self.set_hostapd_parameter(self.HOSTAPD_SSID,  self.get_argument('ZYNTHIAN_WIFI_HOSTAPD_NAME'), hostapd_parameters)

			hostapd_password =  self.get_argument('ZYNTHIAN_WIFI_HOSTAPD_PASSWORD')
			if hostapd_password:
				self.set_hostapd_parameter(self.HOSTAPD_PWD,  hostapd_password, hostapd_parameters)

			if hostapd_password or has_new_name:
				self.hostapd_systemctl("0")

			hostapd_active = self.request.arguments.get('ZYNTHIAN_WIFI_HOSTAPD_ACTIVE','0')[0]

			hostapd_parameters[self.HOSTAPD_SERVICE_ACTIVITY_CHANGED] = self.hostapd_systemctl("1" if has_new_name or hostapd_password else hostapd_active)


	def get_supplicant_file_name(self):
		supplicant_file_name = "/etc/wpa_supplicant/wpa_supplicant.conf"
		#if os.path.getsize(supplicant_file_name) == 0:
		#	supplicant_file_name = "/zynthian/zynthian-sys/etc/wpa_supplicant/wpa_supplicant.conf"
		return supplicant_file_name


	def read_supplicant_data(self, supplicant_file_name):
		try:
			fo = open(supplicant_file_name, "r")
			wpa_supplicant_data = "".join(fo.readlines())
			fo.close()
			return wpa_supplicant_data
		except:
			pass
		return ""


	def apply_updated_fields(self, wpa_supplicant_data, fieldNames):
		supplicant_file_name = self.get_supplicant_file_name()
		if supplicant_file_name:
			previous_supplicant_data = self.read_supplicant_data(supplicant_file_name)

			p = re.compile('.*?network=\\{.*?ssid=\\"(.*?)\\".*?psk=\\"(.*?)\\".*?\\}.*?', re.I | re.M | re.S )
			iterator = p.finditer(previous_supplicant_data)
			for m in iterator:
				action = self.get_argument('ZYNTHIAN_WIFI_ACTION')
				if action and action == 'REMOVE_' + m.group(1):
					print('Removing network')
					pRemove =  re.compile('(.*)network={.*?ssid=\\"' + m.group(1) + '\\".*?}(.*)', re.I | re.M | re.S )
					wpa_supplicant_data = pRemove.sub(r'\1\2', wpa_supplicant_data)
				else:
					newPassword =  self.get_argument('ZYNTHIAN_WIFI_PSK_' + m.group(1))

					mNewSupplicantData = re.match('.*ssid="' + m.group(1) + '".*?psk="(.*?)".*', wpa_supplicant_data, re.I | re.M | re.S)
					if mNewSupplicantData:
						if not newPassword and  not mNewSupplicantData.group(1) == self.PASSWORD_MASK:
							newPassword = mNewSupplicantData.group(1)
					if not newPassword: newPassword = m.group(2)

					pReplacePasswordVeil = re.compile('ssid=\\"' + m.group(1) + '\\"(.*?psk=)\\".*?\\"', re.I | re.M | re.S )
					wpa_supplicant_data = pReplacePasswordVeil.sub('ssid="' + m.group(1) + r'"\1"' + newPassword + '"', wpa_supplicant_data)

					for fieldName in fieldNames:
						fieldUpdated =  self.get_argument(fieldName + '_' + m.group(1) + '_UPDATED')
						if fieldUpdated:
							fieldValue =  self.get_argument(fieldName + '_' + m.group(1))
							regexp = 'ssid=\\"' + m.group(1) + '\\"(?P<pre>.*?' + self.WPA_FIELD_MAP[fieldName] + '=)\\S+(?P<post>.*\\})'
							pReplacement = re.compile(regexp, re.I | re.M | re.S )
							wpa_supplicant_data = pReplacement.sub("ssid=\"" + m.group(1) + "\"" + r'\g<pre>' + str(fieldValue) + r'\g<post> ', wpa_supplicant_data)

		return wpa_supplicant_data


	def add_new_network(self, wpa_supplicant_data, newSSID):
		wpa_supplicant_data += '\nnetwork={\n\tssid="'
		wpa_supplicant_data += newSSID
		wpa_supplicant_data += '"\n\tscan_ssid=1\n\tkey_mgmt=WPA-PSK\n\tpsk=""\n\tpriority=10\n}'
		return wpa_supplicant_data

	def get_hostapd_parameters(self):
		hostapd_parameters = {}
		if os.path.isfile(self.HOSTAPD_FILE):
			with open(self.HOSTAPD_FILE) as hostapd_file:
				for line in hostapd_file:
					(key, value) = line.split("=")
					if key == self.HOSTAPD_SSID:
						hostapd_parameters[key] = value.strip()


		return hostapd_parameters

	def is_hostapd_active(self):
		try:
			result = subprocess.check_output(['systemctl','is-active',self.HOSTAPD_SERVICE])

			if result.strip().decode("utf-8") == "active":
				return "1"
		except subprocess.CalledProcessError as e:
			pass
		return "0"

	def hostapd_systemctl(self, target_value):
		current_value = self.is_hostapd_active();
		try:
			target_value = str(target_value,"UTF-8")
		except:
			pass
		if current_value != target_value:
			try:
				result = subprocess.check_output(['systemctl','start' if target_value == "1" else 'stop',self.HOSTAPD_SERVICE])
				logging.info("%s %s" % (self.HOSTAPD_SERVICE, 'started' if target_value == "1" else 'stopped'))
				return True
			except subprocess.CalledProcessError as e:
				pass
		return False

	def set_hostapd_parameter(self, field, value, old_values):
		try:
			old_value = old_values[field] if field in old_values else ''
			if 	old_value != value:
				logging.info("change value")
				subprocess.call("export NEW_VALUE=%(new_value)s ; sudo sed -i \"s/%(field)s=.*/%(field)s=${NEW_VALUE}/g\" %(file)s" % {'new_value': value, 'field': field, 'file': self.HOSTAPD_FILE}, shell = True)
				old_values[field] = value
				return True
		except subprocess.CalledProcessError as e:
			logging.info(str(e))
		return False
