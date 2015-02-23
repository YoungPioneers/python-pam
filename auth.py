#
#  Author:   huangjunwei@youmi.net
#  Time:     Thu 19 Feb 2015 04:08:49 PM CST
#  File:     auth.py
#  Desc:     pam auth module
#
# -*- coding: encoding -*-

import PAM
import random
import string
import os
import pyotp
import datetime
import time


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_DIR = "%s/secret" % BASE_DIR
LOG = "%s/log/auth.log" % BASE_DIR

service = 'sshd'
auth = PAM.pam()
auth.start(service)


class User(object):
    @property
    def name(self):
        return self._name

    @property
    def secret(self):
        return self._secret

    def __init__(self, name):
        self._name = name

    def authenticate(self, code):
        file_name = os.path.join(SECRET_DIR, self._name)
        if not os.path.exists(file_name):
            return False

        with open(file_name, "r") as fd:
            self._secret = fd.read()

        totp = pyotp.TOTP(self._secret)

        with Timecop(int(time.time())):
            return totp.verify(code)

    def generate_secret(self, length=16):
        chars = string.ascii_letters
        self._secret = ''.join([random.choice(chars) for i in range(length)])
        file_name = os.path.join(SECRET_DIR, self._name)
        with open(file_name, "w+") as fd:
            fd.write(self._secret)
            return True

        return False


class Timecop(object):
    def __init__(self, freeze_timestamp):
        self.freeze_timestamp = freeze_timestamp

    def __enter__(self):
        self.real_datetime = datetime.datetime
        datetime.datetime = self.frozen_datetime()

    def __exit__(self, type, value, traceback):
        datetime.datetime = self.real_datetime

    def frozen_datetime(self):
        class FrozenDateTime(datetime.datetime):
            @classmethod
            def now(cls):
                return cls.fromtimestamp(timecop.freeze_timestamp)

        timecop = self
        return FrozenDateTime


def log(action, msg):
    with open(LOG, "a") as fd:
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = "%s [%s] %s\n" % (now, action, msg)
        fd.write(msg)


def pam_sm_authenticate(pamh, flags, args):
    try:
        sys_user = pamh.get_user(None)

        message = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "name: ")
        rsp = pamh.conversation(message)
        name = rsp.resp

        message = pamh.Message(pamh.PAM_PROMPT_ECHO_OFF, "code: ")
        rsp = pamh.conversation(message)
        code = rsp.resp

        dynamic_user = User(name)

    except pamh.exception, e:
        return e.pam_result

    if sys_user is not None and dynamic_user.authenticate(code):
        msg = "%s login as %s success" % (name, sys_user)
        log("auth", msg)
        pamh.env["user_name"] = name

        return pamh.PAM_SUCCESS
    else:
        msg = "%s login as %s fail" % (name, sys_user)
        log("auth", msg)
        return pamh.PAM_SYSTEM_ERR


def pam_sm_setcred(pamh, flags, args):
    # when flags is 4, it means close session
    if 4 == flags:
        sys_user = pamh.get_user(None)
        msg = "%s logout as %s success" % (pamh.env["user_name"], sys_user)
        log("auth", msg)

    return pamh.PAM_SUCCESS
