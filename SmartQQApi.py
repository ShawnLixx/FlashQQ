#-*- coding:utf-8 –*-

import requests
from StringIO import StringIO
from PIL import Image
import time
import json


class webQQ:
	def __init__(self):
		self.headers = {'User-Agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'''}
		self.loginurl = '''http://w.qq.com'''
		self.qrcodeurl = '''https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=0.1'''

		self.session = requests.Session()
		self.session.headers.update(self.headers)

		#open login url
		self.session.get(url = self.loginurl)

		self.msg_id = 65450001
		self.t = 1459950706179
		
	#hash algorithm, it'll be used while getting friends list etc. 
	def hash(self, b, j):
		a = [0,0,0,0]  
		for i in range(0,len(j)):  
			a[i%4] ^= ord(j[i])  
		w = ["EC","OK"]  
		d = [0,0,0,0]  
		d[0] = int(b) >> 24 & 255 ^ ord(w[0][0])  
		d[1] = int(b) >> 16 & 255 ^ ord(w[0][1])  
		d[2] = int(b) >> 8 & 255 ^ ord(w[1][0])  
		d[3] = int(b) & 255 ^ ord(w[1][1])  
		w = [0,0,0,0,0,0,0,0]  
		for i in range(0,8):  
			if i%2 == 0:  
				w[i] = a[i>>1]  
			else:  
				w[i] = d[i>>1]  
		a = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]  
		d = ""  
		for i in range(0,len(w)):  
			d += a[w[i]>>4&15]  
			d += a[w[i]&15]  
		return d  

	#return an Image object contains qrcode picture in png
	def getQrcode(self):

		#get qrcode
		try:
			self.r = self.session.get(url = self.qrcodeurl)
		except:
			print "get qrcode error"
			exit()
		self.qrcodeImg = Image.open(StringIO(self.r.content))
		return self.qrcodeImg

	#check whether user has scaned qrcode
	#return value:1, logined in. 2, user scaned the qrcode and hasn't click "login".
	#3, qrcode still valid and user has not logined in. 4, qrcode is invalid, please request another qrcode.
	#5, http error.
	def isLoginIn(self):
		#check whether login in
		self.whetherLoginurl = '''https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-12029&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10152&login_sig=&pt_randsalt=0'''
		self.session.headers['Referer'] = '''https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'''

		self.r = self.session.get(url = self.whetherLoginurl)
		if self.r.status_code != 200:
			return 5
		elif self.r.text.encode('utf-8').find("二维码认证中") != -1:
			return 2
		elif self.r.text.encode('utf-8').find("二维码未失效") != -1:
			return 3
		elif self.r.text.encode('utf-8').find("二维码已失效") != -1:
			return 4
		else:
			return 1

	#this an very important step, use this function before you want to get friends list or send/get messages. return 1 when succeed
	def getImportInfo(self):
		#get ptwebqq
		self.startIndex = self.r.text.find("http:")
		self.endIndex = self.r.text.encode('utf-8').find('''\','0','登录成功！\'''')
		self.ptwebqqUrl = self.r.text[self.startIndex:self.endIndex]

		self.session.headers['Referer'] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.r = self.session.get(url = self.ptwebqqUrl)

		self.ptwebqq = self.session.cookies.get_dict()['ptwebqq']

		#get vfwebqq
		self.vfwebqqUrl = '''http://s.web2.qq.com/api/getvfwebqq?ptwebqq=''' + self.ptwebqq + '''&clientid=53999199&psessionid=&t=0.1'''
		self.r = self.session.get(url = self.vfwebqqUrl)
		self.vfwebqqRe = json.loads(self.r.text)
		self.vfwebqq = self.vfwebqqRe['result']['vfwebqq']

		#get psessionid and uin
		self.psessionUrl = '''http://d1.web2.qq.com/channel/login2'''
		self.requestData = {}
		self.clientid = 53999199
		self.rData = {'ptwebqq': self.ptwebqq, 'clientid': self.clientid, 'psessionid': '', 'status': 'online'}
		self.requestData['r'] = json.dumps(self.rData)
		self.session.headers['Referer'] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.r = self.session.post(url = self.psessionUrl, data = self.requestData)
		self.returnJson = json.loads(self.r.text)
		self.psessionid = self.returnJson['result']['psessionid']
		self.uin = self.returnJson['result']['uin']
		return 1

	#return a dict of friends, the key is uin of the friend, and the value is a dict, contents 'nick'(qq nickname, str), 'markname'(str), 'categories'(id of categories), 'vipinfo'(a dict, contains 'vip_level'(num), 'is_vip'(0 for not))
	#an addition key of the dict is 'categories', the value of it is a list of categorie, very categorie is a dict containing 'sort'(the orler number of the categorie), 'name'(str)
	#return 0 when failed.
	def getFriendsList(self):
		
		#get friends list
		self.getFriendsListUrl = '''http://s.web2.qq.com/api/get_user_friends2'''
		self.session.headers["Referer"] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.rFriendsData = {"vfwebqq": self.vfwebqq, "hash": self.hash(self.uin, self.ptwebqq)}
		self.requestData["r"] = json.dumps(self.rFriendsData)
		self.r = self.session.post(url = self.getFriendsListUrl, data = self.requestData)
		if self.r.status_code != 200:
			return 0
		self.friendsList = json.loads(self.r.text)
		if self.friendsList["retcode"] != 0:
			return 0

		#friends is a dict, key is uin
		self.friends = {}
		for info in self.friendsList['result']['info']:
			self.friends[info["uin"]] = {}
			self.friends[info["uin"]]["nick"] = info["nick"]
		for mark in self.friendsList['result']['marknames']:
			self.friends[mark["uin"]]["markname"] = mark["markname"]
		'''for vipinfo in self.friendsList['result']['vipinfo']:
			self.friends[vipinfo["u"]]["vipinfo"]["is_vip"] = vipinfo["is_vip"]
			self.friends[vipinfo["u"]]["vipinfo"]["vip_level"] = vipinfo["vip_level"]'''
		for info in self.friendsList["result"]["friends"]:
			self.friends[info["uin"]]["categories"] = info["categories"]
		self.friendsList["result"]["categories"].sort(key = lambda x:x['sort'])
		self.friendsList["categories"] = []
		for info in self.friendsList["result"]["categories"]:
			self.friendsList["categories"].append(info)
		return self.friends

	#like getFriendsList
	def getGroupList(self):
		self.getGroupListUrl = '''http://s.web2.qq.com/api/get_group_name_list_mask2'''
		self.session.headers["Referer"] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.rGroupData = {"vfwebqq": self.vfwebqq, "hash": hash(self.uin, self.ptwebqq)}
		self.requestData["r"] = json.dumps(self.rGroupData)
		self.r = self.session.post(url = self.getGroupListUrl, data = self.requestData)
		if self.r.status_code != 200:
			return 0
		self.groupList = self.json.loads(self.r.text)
		if self.groupList["retcode"] != 0:
			return 0
		self.groups = {}
		for info in self.groupList['result']['gnamelist']:
			self.groups[info['gid']] = {}
			self.groups[info['gid']]["name"] = info["name"]
			self.groups[info['gid']]["code"] = info["code"]
		for info in self.groupList['result']['gmasklist']:
			self.groups[info['uin']]["markname"] = info["markname"]
		return self.groups

	#like getGroupList
	def getDiscussList(self):
		self.getDiscussListUrl = '''http://s.web2.qq.com/api/get_discus_list'''
		self.session.headers["Referer"] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.rDiscussData = {"vfwebqq": self.vfwebqq, "clientid": self.clientid, "psessionid": self.psessionid}
		self.r = self.session.get(url = self.getDiscussListUrl, data = self.rDiscussData)
		if self.r.status_code != 200:
			return 0
		self.discussList = self.json.loads(self.r.text)
		if self.discussList["retcode"] != 0:
			return 0
		self.discusses = {}
		for info in self.GroupList['result']['dnamelist']:
			self.discusses[info['did']] = {}
			self.discusses[info['did']]["name"] = info["name"]
		return self.discusses


	#return a list of messages(a dict), contains 'uin'(the uin of senders), 'type'(str, 'group', 'discuss' or 'friend'), 'time', 'content'
	def getMessages(self):

		self.getMessagesUrl = '''http://d1.web2.qq.com/channel/poll2'''
		self.rData['psessionid'] = self.psessionid
		self.requestData['r'] = json.dumps(self.rData)
		self.session.headers['Referer'] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.session.headers['Host'] = '''d1.web2.qq.com'''
		self.session.headers['Origin'] = '''http://d1.web2.qq.com'''
		self.r = self.session.post(url = self.getMessagesUrl, data = self.requestData)
		try:
			self.results = json.loads(self.r.text)
		except:
			return 0
		if self.results.has_key("errmsg"):
			return 1
		else:
			self.results = json.loads(self.r.text)["result"]
		self.messages = []
		for result in self.results:
			message = {}
			message["uin"] = result["value"]["from_uin"]
			message["font"] = result["value"]["content"][0][1]
			message["time"] = result["value"]["time"]
			message["content"] = ""
			if result["poll_type"] == "message":
				message["type"] = "friend"
			elif result["poll_type"] == "group_message":
				message["type"] = "group"
			elif result["poll_type"] == "discu_message":
				message["type"] = "discuss"
			for item in result["value"]["content"]:
				if isinstance(item, unicode):
					message["content"] = message["content"] + item
				elif isinstance(item, list):
					if isinstance(item[1], int):
						message["content"] = message["content"] + '[face,' + item[1] + ']'
			self.messages.append(message)
		return self.messages

	#return 1 when sent succeed, 0 otherwise
	def	sendMsgFriend(self, toUin, content):
		self.sendMsgFriendUrl = '''http://d1.web2.qq.com/channel/send_buddy_msg2'''
		self.session.headers["Referer"] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.sendData = '{\"to\": '+ str(toUin) + ', \"content\": \"' + content + '\", \"face\": 459, \"clientid\": ' + str(self.clientid) + ', \"msg_id\": ' + str(self.msg_id) + ', \"psessionid\": \"' + str(self.psessionid) + '\"}'
		self.sendRequest = {}
		self.sendRequest['r'] = self.sendData
		self.sendR = self.session.post(url = self.sendMsgFriendUrl, data = self.sendRequest)
		self.R = json.loads(self.sendR.text)
		if self.R.has_key("msg"):
			return 1
		else:
			return 0

	#return 1 when sent succeed, 0 otherwise
	def	sendMsgGroup(self, toGid, content):
		self.sendMsgGroupUrl = '''http://d1.web2.qq.com/channel/send_qun_msg2'''
		self.session.headers["Referer"] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.sendData = '{\"group_uin\": '+ str(toUin) + ', \"content\": \"' + content + '\", \"face\": 459, \"clientid\": ' + str(self.clientid) + ', \"msg_id\": ' + str(self.msg_id) + ', \"psessionid\": \"' + str(self.psessionid) + '\"}'
		self.sendRequest = {}
		self.sendRequest['r'] = self.sendData
		self.sendR = self.session.post(url = self.sendMsgGroupUrl, data = self.sendRequest)
		self.R = json.loads(self.sendR.text)
		if self.R.has_key("msg"):
			return 1
		else:
			return 0

	#return 1 when sent succeed, 0 otherwise
	def	sendMsgDiscuss(self, toDid, content):
		self.sendMsgDiscussUrl = '''http://d1.web2.qq.com/channel/send_qun_msg2'''
		self.session.headers["Referer"] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.sendData = '{\"did\": '+ str(toUin) + ', \"content\": \"' + content + '\", \"face\": 459, \"clientid\": ' + str(self.clientid) + ', \"msg_id\": ' + str(self.msg_id) + ', \"psessionid\": \"' + str(self.psessionid) + '\"}'
		self.sendRequest = {}
		self.sendRequest['r'] = self.sendData
		self.sendR = self.session.post(url = self.sendMsgDiscussUrl, data = self.sendRequest)
		self.R = json.loads(self.sendR.text)
		if self.R.has_key("msg"):
			return 1
		else:
			return 0

	#get online info only online user will be shown in this dict
	def getOnlinInfo(self):
		self.getOnlinInfoUrl = '''http://d1.web2.qq.com/channel/get_online_buddies2'''
		self.requestData = {'vfwebqq': self.vfwebqq, 'clientid': self.clientid, 'psessionid': self.psessionid, 't': self.t}
		self.session.headers['Referer'] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.r = self.session.get(url = self.getOnlinInfoUrl, data = self.requestData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response["retcode"] != 0:
			return 0
		self.isOnline = {}
		for info in self.response:
			self.isOnline[info["uin"]] = {}
			#status can be "online", "busy", "away", "slient", etc..
			self.isOnline[info["uin"]]["status"] = info["status"]
			#need to fix
			self.isOnline[info["uin"]]["client_type"] = info["client_type"]
		return isOnline

	#get recent list
	def getRecentList(self):
		self.getRecentListUrl = '''http://d1.web2.qq.com/channel/get_recent_list2'''
		self.sendData = {'vfwebqq': self.vfwebqq, 'clientid': self.clientid, 'psessionid': self.psessionid}
		self.sendRequest = {}
		self.sendRequest['r'] = json.dumps(self.sendData)
		self.session.headers['Referer'] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.r = self.session.post(url = self.getRecentListUrl, data = self.sendRequest)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		self.recentList = [] = self.response['result']
		return recentList

	def getQQNumber(self, uin):
		self.getQQNumberUrl = '''http://s.web2.qq.com/api/get_friend_uin2?'''
		self.sendData = {'tuid': uin, 'type': 1, 'vfwebqq': self.vfwebqq, 't': self.t}
		self.session.headers['Referer'] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.r = self.session.get(url = self.getQQNumberUrl, data = self.sendData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		return self.response['result']['account']


	def getFriendInfo(self, uin):
		self.getFriendInfoUrl = '''http://s.web2.qq.com/api/get_friend_info2'''
		self.sendData = {'tuid': uin, 'type': 1, 'vfwebqq': self.vfwebqq, 't': self.t, 'clientid': self.clientid, 'psessionid': self.psessionid}
		self.session.headers['Referer'] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.r = self.session.get(url = self.getFriendInfoUrl, data = self.sendData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		self.friendInfo = self.response['result']
		return friendInfo

	def getSelfInfo(self):
		self.getSelfInfoUrl = '''http://s.web2.qq.com/api/get_self_info2'''
		self.sendData = {'t': self.t}
		self.session.headers['Referer'] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.r = self.session.get(url = self.getSelfInfoUrl, data = self.sendData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		self.selfInfo = self.response['result']
		return selfInfo

	#return groupList, return 0 when failed
	def getGroupInfo(self, code):
		self.getGroupInfoUrl = '''http://s.web2.qq.com/api/get_group_info_ext2'''
		self.sendData = {'gcode': code, 'vfwebqq': self.vfwebqq, 't': self.t}
		self.session.headers['Referer'] = '''http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'''
		self.r = self.session.get(url = self.getGroupInfoUrl, data = self.sendData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		self.groupInfo = self.response['result']['ginfo']
		self.groupInfo['members'] = {}
		for info in self.response['result']['minfo']:
			self.groupInfo['members'][info['uin']] = {}
			self.groupInfo['members'][info['uin']]['nick'] = info['nick']
			self.groupInfo['members'][info['uin']]['province'] = info['province']
			self.groupInfo['members'][info['uin']]['gender'] = info['gender']
			self.groupInfo['members'][info['uin']]['country'] = info['country']
			self.groupInfo['members'][info['uin']]['city'] = info['city']

		for info in self.response['result']['stats']:
			self.groupInfo['members'][info['uin']]['client_type'] = info['client_type']
		for info in self.response['result']['cards']:
			self.groupInfo['members'][info['muin']]['groupCard'] = info['card']
		for info in self.response['result']['cards']:
			self.groupInfo['members'][info['u']]['is_vip'] = info['is_vip']
			self.groupInfo['members'][info['u']]['vip_level'] = info['vip_level']
		return self.groupInfo


	#return discussinfo, return 0 when failed
	def getDiscussInfo(self, did):
		self.getDiscussInfoUrl = '''http://d1.web2.qq.com/channel/get_discu_info'''
		self.sendData = {'did': did, 'vfwebqq': self.vfwebqq, 't': self.t, 'clientid': self.clientid, 'psessionid': self.psessionid}
		self.session.headers['Referer'] = '''http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'''
		self.r = self.session.get(url = self.getDiscussInfoUrl, data = self.sendData)
		if self.r.status_code != 200:
			return 0
		self.response = json.loads(self.r.text)
		if self.response['retcode'] != 0:
			return 0
		self.discussInfo = {}
		self.discussinfo['name'] = self.response['resutl']['info']['discu_name']
		self.groupInfo['members'] = {}
		for info in self.response['result']['info']['mem_list']:
			self.groupInfo['members'][info['mem_uin']] = {}
		for info in self.response['result']['mem_info']:
			self.groupInfo['members'][info['uin']]['nick'] = info['nick']
		for info in self.response['result']['mem_status']:
			self.groupInfo['members'][info['uin']]['client_type'] = info['client_type']
			self.groupInfo['members'][info['uin']]['status'] = info['status']
