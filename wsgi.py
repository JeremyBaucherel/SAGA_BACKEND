# -*- coding: utf-8 -*-

"""Tornado HTTP daemon to serve ASGARD BACKEND"""

import os.path
import sqlalchemy.orm
import sys
import urllib

ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)))

sys.path.append(os.path.join(ROOT_PATH, u"./libs"))
sys.path.append(os.path.join(ROOT_PATH, u"./sy_httpd"))

import sqlalchemy
import tornado.web
import tornado.wsgi

import config
import web
import web.handler
import web.handler.generic
import web.handler.user
import web.handler.metallisation
import web.handler.optique
import web.handler.parametre

#sqlApp = sqlServer.sqlServer(config.serverapp, config.databaseapp)
#DB_ENGINE = sqlApp.connexion()

#DB_ENGINE = sqlalchemy.create_engine(u"Driver={SQL Server};Server=NZLX302093813\SQLEXPRESS;Database=" + config.databaseapp, poolclass=sqlalchemy.pool.QueuePool)
#DB_ENGINE = sqlalchemy.create_engine('postgresql//NZLX302093813:SQLEXPRESS/' + config.databaseapp)

DB_ENGINE = sqlalchemy.create_engine('mssql://NZLX302093813\\SQLEXPRESS/' + config.databaseapp + '?trusted_connection=yes&driver=ODBC+Driver+13+for+SQL+Server') 

"""
try:
    session = sqlalchemy.orm.sessionmaker(bind=DB_ENGINE)()
    for row in session.execute(u"SELECT * FROM users"):
        print(row)
    print(" -> OK")
except Exception as e:
    print("DB CON FAILED!", e)
"""

web_app = tornado.web.Application(
    web.ROUTES + [(r'/.*$', web.handler.JsonHandler)],
    db_engine=DB_ENGINE
)
APP = tornado.wsgi.WSGIAdapter(web_app)

if __name__ == "__main__":
    import tornado.ioloop
    web_app.listen(config.HTTP_PORT)
    tornado.ioloop.IOLoop.instance().start()
