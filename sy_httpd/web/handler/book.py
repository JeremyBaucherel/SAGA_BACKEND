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


