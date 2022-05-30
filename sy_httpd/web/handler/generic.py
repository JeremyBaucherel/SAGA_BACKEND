# -*- coding: utf-8 -*-
import tornado.escape
import web.handler
import web.handler.fonction as fct

    

@web.route(u"/api/ping")
class PingHandler(web.handler.JsonHandler):

    def get(self):
        self.write_json({u"ping": u"pong"})
