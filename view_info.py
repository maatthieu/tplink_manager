# -*- coding: utf8 -*-
"""
Send SMS via TP-Link TL-MR6400.
This code shows how to send an SMS using the admin GUI of the above router.
FIXME TODO add error handling, logging
Author: Fabio Pani <fabiux@fabiopani.it>
License: see LICENSE
"""
from hashlib import md5
from base64 import b64encode
from datetime import datetime
from time import strftime
import json
import requests
import time

# SMS
router_domain = '192.168.2.1'  # set actual IP or hostname of your router
router_url = 'http://' + router_domain + '/'
router_login_path = 'userRpm/LoginRpm.htm?Save=Save'
router_sms_referer = '/userRpm/_lte_SmsNewMessageCfgRpm.htm'
router_sms_action = '/userRpm/lteWebCfg'
router_status = '/userRpm/StatusRpm.htm'

router_admin = 'admin'  # set admin username
router_pwd = 'admin'  # set admin password


def check_connection():
   
    status_json = '{"module":"status","action":0}'
    # authentication
    authstring = router_admin + ':' + md5(router_pwd.encode('utf-8')).hexdigest()
    authstring = 'Basic ' + b64encode(authstring.encode('utf-8')).decode('utf-8')
    cookie = {'Authorization': authstring, 'Path': '/', 'Domain': router_domain}
    s = requests.Session()
    r = s.get(router_url + router_login_path, cookies=cookie)
    if r.status_code != 200:
        # FIXME TODO log errors
        exit()
    hashlogin = r.text.split('/')[3]
    status_page = router_url + hashlogin + router_status
    s.headers.update({'referer': status_page})
    #res = s.get(status_page)
    #print res.text

    # Get status
    status_form_page = router_url + hashlogin + router_sms_action
    res = s.post(status_form_page, status_json, cookies=cookie)
    return res


def send_sms(phone_num, msg):
    """
    Send an SMS via TP-Link TL-MR6400.
    :param phone_num: recipient's phone number
    :type phone_num: str
    :param msg: message to send
    :type msg: str
    """
    # SMS payload
    sms = {'module': 'message',
           'action': 3,
           'sendMessage': {
               'to': phone_num,
               'textContent': msg,
               'sendTime': strftime('%Y,%-m,%-d,%-H,%-M,%-S', datetime.now().timetuple())
           }}

    # authentication
    authstring = router_admin + ':' + md5(router_pwd.encode('utf-8')).hexdigest()
    authstring = 'Basic ' + b64encode(authstring.encode('utf-8')).decode('utf-8')
    cookie = {'Authorization': authstring, 'Path': '/', 'Domain': router_domain}
    s = requests.Session()
    r = s.get(router_url + router_login_path, cookies=cookie)
    if r.status_code != 200:
        # FIXME TODO log errors
        exit()
    hashlogin = r.text.split('/')[3]
    sms_form_page = router_url + hashlogin + router_sms_referer
    sms_action_page = router_url + hashlogin + router_sms_action

    # send SMS
    s.headers.update({'referer': sms_form_page})
    r = s.post(sms_action_page, json=sms, cookies=cookie)
    if r.status_code != 200:
        # FIXME TODO log errors
        pass

#send_sms('0630633918', 'test from pi')
while True:
    res = check_connection()
    print res.text

    dlTaux = res.json()["wan"]["rxSpeed"]
    print str(int(float(dlTaux) / 1024)) + "Ko"

    time.sleep(1)




#http://192.168.2.1/NAUVZEAAFXZZYTSC/userRpm/SysRebootRpm.htm?Reboot=Reboot


