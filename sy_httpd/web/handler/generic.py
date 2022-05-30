# -*- coding: utf-8 -*-
import tornado.escape
import web.handler
import web.handler.fonction as fct

# Menu déroulant qui liste les pgms
@web.route(u"/api/pgm")
class pgmCfmHandler(web.handler.JsonHandler):

    def get(self):
        self.write_json(fct.result_requete_FormList(self, "SELECT id, nom FROM pgm"))
        

@web.route(u"/api/ping")
class PingHandler(web.handler.JsonHandler):

    def get(self):
        self.write_json({u"ping": u"pong"})
