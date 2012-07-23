#!/usr/bin/python
# -*- coding: utf-8; -*-
#
# Copyright 2012 Juliano Martinez
# Copyright 2012 Diego Souza
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
# @author: Juliano Martinez
# @author: Diego Souza

import math
import funcs as f
import copycats
from datetime import datetime
from nose.tools import *
from leela import config
from leela import funcs

def test_lasergun_replies_timestamp_when_everything_goes_fine():
    prefix    = "%s|timestamp||" % f.rand_hostname()
    service   = "timestamp"
    metrics   = [("pi", str(math.pi))]
    cassandra = copycats.Storage()
    with f.lasergun_ctx(cassandra) as (send,recv):
        send(prefix + "||".join(map("|".join, metrics)))
        ok_(float(recv()[0]) > 0)


def test_lasergun_replies_error_when_something_fails():
    hostname  = f.rand_hostname()
    cassandra = copycats.Storage()
    with f.lasergun_ctx(cassandra) as (send,recv):
        send("noise")
        eq_("error", recv()[0])
