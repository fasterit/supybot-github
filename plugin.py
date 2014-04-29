#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#

import re
import json
import time
import Queue
import urllib
import urlparse
import threading
import BaseHTTPServer

import supybot.log as log
import supybot.conf as conf
import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

import local.globals as globals
import local.handler.GithubHandler as RequestHandler
import local.utility as Utility

globals.init()


class Github(callbacks.Plugin):
    """Add the help for \"@plugin help Github\" here
    This should describe how to use this plugin."""

    threaded = True
    port     = Utility.configValue('port')
    messages = []
    pass

    def ServerStart(self, httpd):
        try:
            log.info('Server Starts - %s:%s' % ('', self.port))
            httpd.serve_forever()
        except:
            return

    def __init__(self, irc):
        self.__parent = super(Github, self)
        self.__parent.__init__(irc)
        server_class = BaseHTTPServer.HTTPServer
        self.httpd = server_class(('', self.port), RequestHandler.GithubHandler)
        t = threading.Thread(target=self.ServerStart, args=(self.httpd,))
        t.daemon = False
        t.start()

    def __call__(self, irc, msg):
        self.__parent.__call__(irc, msg)


    def die(self):
        self.httpd.server_close()
        self.httpd.shutdown()
        self.__parent.die()
        reload(RequestHandler)
        reload(Utility)

    def get(self, irc, msg, args, order, type, garbage):
        """[<order>] [<type>] [<garbage>]
        Returns the requested message generated by the request handler.
        Examples: get first message, get 2nd last response
        """
        _digits = re.compile('\d')

        orders = { 'first': 1,
                   'second': 2,
                   'third': 3,
                   'fourth': 4
                 }

        if _digits.search(order):
            requestedNum = int(re.sub("[^0-9]", "", order))
        else:
            requestedNum = orders[order] if order in orders else 1

        if order == 'last' or type == 'last':
            requestedNum = len(globals.messageList) - requestedNum + 1

        try:
            irc.reply(globals.messageList[requestedNum-1])
        except IndexError:
            irc.error('No such message')

    # Debug command
    get = wrap(get, ['lowered', optional('lowered'), optional('text')]) if world.testing else False


Class = Github

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
