#!/usr/bin/env python
#
#  Author:   huangjunwei@youmi.net
#  Time:     Mon 23 Feb 2015 09:44:57 PM CST
#  File:     add_user.py
#  Desc:     ./add_user.py --name somebody
#
# -*- coding: encoding -*-

import sys

if "__main__" == __name__:
    if len(sys.argv) != 2:
        print "./add_user.py somebody"
    else:
        import auth
        user = auth.User(sys.argv[1])
        user.generate_secret()
        print user.secret
