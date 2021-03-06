# -*- coding: utf-8; -*-
#
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

import time
from leela.server import funcs
from leela.server.data import pp
from leela.server.data import parser
from leela.server.data import event
from leela.server.data import data

DEFAULT_EPOCH = 2000

def serialize_key(y, mo, d, h, mi, s, epoch):
    e = funcs.timetuple_timestamp((epoch, 1, 1, 0, 0, 0))
    t = funcs.timetuple_timestamp((y, mo, d, h, mi, s))
    return(t - e)

def unserialize_key(k, epoch):
    e = funcs.timetuple_timestamp((epoch, 1, 1, 0, 0, 0))
    t = funcs.datetime_fromtimestamp(k + e)
    return(t.year, t.month, t.day, t.hour, t.minute, t.second)

def serialize_event(e, epoch):
    timestamp = (e.year(), e.month(), e.day(), e.hour(), e.minute(), e.second())
    k = serialize_key(*timestamp, epoch=epoch)
    v = e.value()
    return((k, v))

def serialize_data(e, epoch):
    timestamp = (e.year(), e.month(), e.day(), e.hour(), e.minute(), e.second())
    k = serialize_key(*timestamp, epoch=epoch)
    v = pp.render_json(e.value())
    return((k, v))

def unserialize_event(name, k, v, epoch):
    timetuple = list(unserialize_key(k, epoch=epoch))
    timestamp = funcs.timetuple_timestamp(timetuple)
    return(event.Event(name, v, timestamp))

def unserialize_data(name, k, v, epoch):
    timetuple = list(unserialize_key(k, epoch=epoch))
    timestamp = funcs.timetuple_timestamp(timetuple)
    return(data.Data(name, parser.parse_json(v), timestamp))
