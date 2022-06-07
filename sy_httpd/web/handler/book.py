from asyncio.windows_events import NULL
from typing import Any, Dict, List, Optional, Tuple
from xmlrpc.client import boolean
from mypy_extensions import TypedDict
import hashlib
import random
import sendmail
import string
import tornado
import uuid
import datetime
import config
import web.handler
import saga_db

@web.route(u"/api/book/dashboard")
class DashboardHandler(web.handler.JsonHandler):
    class JsonDashboard(TypedDict):
        id: int
        id_type: int
        name_type: str
        id_saga: int
        name_saga: str
        number: str
        name: str
        id_book_publishing: int
        name_book_publishing: str
        id_owner: int
        name_owner: str
        id_location: int
        name_location: str

    def get(self):

        user_id = self.user[u"id"]

        out = web.handler.JsonResponse[DashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"BOOK:DISPLAY")

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.Bibliotheque) \
                .outerjoin(saga_db.Type) \
                .outerjoin(saga_db.Emplacement) \
                .outerjoin(saga_db.Proprietaire) \
                .outerjoin(saga_db.Saga) \
                .outerjoin(saga_db.MaisonEdition)

            dashboard=[]
            
            for dash in qry.all(): 
                dashboard.append({
                    u"id": dash.id,
                    u"id_type": dash.id_type,
                    u"name_type": dash.Type.name_type,
                    u"id_saga": dash.id_saga if dash.id_saga else -1,
                    u"name_saga": dash.Saga.name_saga if dash.Saga else "",
                    u"number": dash.number,
                    u"name": dash.name,
                    u"id_book_publishing": dash.id_book_publishing if dash.id_book_publishing else -1,
                    u"name_book_publishing": dash.MaisonEdition.name_book_publishing if dash.MaisonEdition else "",
                    u"id_owner": dash.id_owner if dash.id_owner else -1,
                    u"name_owner": dash.Proprietaire.name_owner if dash.Proprietaire else "",
                    u"id_location": dash.id_location if dash.id_location else -1,
                    u"name_location": dash.Emplacement.name_location if dash.Emplacement else "",
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())


@web.route(u"/api/book/dashboard/edit")
class DashboardEditHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque()
            print("Add a coder...")




@web.route(u"/api/book/dashboard/add")
class DashboardAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque()
            print("Edit a coder...")




@web.route(u"/api/book/dashboard/del")
class DashboardDelHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        delRow = params.get("delRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            # Sélection de la ligne ID à supprimer
            param = self.db_session.query(saga_db.Bibliotheque()).filter_by(id=delRow).first()

            # Suppression de la ligne
            self.db_session.delete(param)

            # Confirmer la suppression
            self.db_session.commit()


@web.route("/api/book/liste/type")
class TypeHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Type) \
                .order_by(saga_db.Type.name_type)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_type,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/book/liste/saga")
class SagaHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Saga) \
                .order_by(saga_db.Saga.name_saga)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/book/liste/publishing")
class PublishingHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.MaisonEdition) \
                .order_by(saga_db.MaisonEdition.name_book_publishing)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_book_publishing,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/book/liste/owner")
class OwnerHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Proprietaire) \
                .order_by(saga_db.Proprietaire.name_owner)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/book/liste/location")
class LocationHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Emplacement) \
                .order_by(saga_db.Emplacement.name_location)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_location,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())