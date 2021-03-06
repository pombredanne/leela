# -*- coding: utf-8 -*-

from leela.server.trial import helpers
import contextlib
import itertools
import threading
import argparse
import tempfile
import select
import random
import socket
import time
import sys
import os

SEED = "leela.dmproc.trial_dmproc"

def mkload(opts, fh):
    opts.load = int(opts.load * 1000 * 1000)
    k         = helpers.strings(SEED, opts.ksize)
    s         = opts.load
    m         = helpers.progress()
    helpers.debug("generating load test file ... [ksize: %s, pktsz: %s, keylen: %s, load: %s]\n" % (helpers.fmt(len(k)),
                                                                                                    helpers.fmt(opts.pktsz),
                                                                                                    len(k[0]),
                                                                                                    helpers.fmt(s)))
    while (s > 0):
        p = []
        c = opts.pktsz
        while (True):
            i  = opts.load - s
            n  = k[i % len(k)]
            l  = "event %s|%s %d.0 %s;" % (len(n), n, i, repr(random.random()))
            z  = len(l)
            s -= 1
            c -= z
            if (c >= 0):
                m.measure(z)
                p.append(l)
            else:
                if (opts.pktsz < z):
                    m.measure(z)
                    p.append(l)
                break
            m.dump_state("mkload")
        fh.write("".join(p) + "\n")
    m.done()

def trial(opts):
    with helpers.with_tempfile() as fh:
        mkload(opts, fh)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM, 0)
        m = helpers.progress()
        helpers.debug("starting load test [sending file] ... \n")
        fh.seek(0)
        for l in fh:
            l = l.strip()
            m.measure(len(l))
            m.dump_state("trial")
            s.sendto(l, 0, opts.databus)
        m.done()

if (__name__ == "__main__"):
    args = argparse.ArgumentParser()
    args.add_argument("--ksize",
                      type    = int,
                      default = 1000000,
                      dest    = "ksize",
                      help    = "number of distinct keys to generate [default: %(default)s]")
    args.add_argument("--load",
                      type    = float,
                      default = 1,
                      dest    = "load",
                      help    = "load size (M) [default: %(default)s]")
    args.add_argument("--pktsz",
                      type    = int,
                      default = 25000,
                      dest    = "pktsz",
                      help    = "apromixate size of the udp package %(default)s")
    args.add_argument("--databus",
                      type    = str,
                      default = "/tmp/databus",
                      dest    = "databus",
                      help    = "the unix socket to connect to [default: %(default)s]")
    trial(args.parse_args())
