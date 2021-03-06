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

import json
from leela.server.data import event
from leela.server.data import data

def render_json(x):
    return(json.dumps(x, allow_nan=True, sort_keys=True))

def render_event(e):
    return("event %d|%s %s %d.0;" % (len(e.name()), e.name(), repr(e.value()), e.unixtimestamp()))

def render_metric(m):
    return("%s %d|%s %s %s;" % (m.type(), len(m.key), m.key, repr(m.val), repr(m.time)))

def render_metrics(ms):
    return("".join(map(render_metric, ms)))

def render_data(e):
    value = render_json(e.value())
    return("data %d|%s %d|%s %d.0;" % (len(e.name()), e.name(), len(value), value, e.unixtimestamp()))

def render_events(es):
    return("".join(map(render_event, es)))

def render_storable(s):
    if isinstance(s, event.Event):
        return(render_event(s))
    elif isinstance(s, data.Data):
        return(render_data(s))
    else:
        raise(RuntimeError())

def render_storable_to_json(e):
    return({"name": e.name(), "value": e.value(), "timestamp": e.unixtimestamp()})

def render_storables_to_json(es):
    return(map(render_storable_to_json, es))

def render_metric_to_json(m):
    return({"type": m.type(), "name": m.key, "value": m.val, "timestamp": m.time})

def render_metrics_to_json(ms):
    return(map(render_metric_to_json, ms))

def render_select(proc, regex):
    return("SELECT %s FROM %s;" % (proc, regex))

def render_storables(ss):
    return("".join(map(render_storable, ss)))
