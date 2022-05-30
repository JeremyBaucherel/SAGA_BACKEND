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
import asgard_db




@web.route(u"/api/optique/dashboard")
class DashboardHandler(web.handler.JsonHandler):
    class JsonDashboard(TypedDict):
        pgm: str
        msn: int
        gamme: str
        cptGrGam: int
        prepaSap: bool
        ordreFabrication: str
        prepaPV: bool
        prepaPdf: bool
        majSap: bool
        datePrepaSap: datetime.datetime
        dateAddOf: datetime.datetime
        dateMajPV: datetime.datetime
        statutScript: str

    def get(self):

        user_id = self.user[u"id"]

        out = web.handler.JsonResponse[DashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"OPTIQUE:DISPLAY")

        if out.ok() and user_id:

            qry = self.db_session.query(asgard_db.ProcessPV) \
                .join(asgard_db.RoutingGTI) \
                .join(asgard_db.UsersRoutingGTI) \
                .join(asgard_db.ProcessRoutingGTI) \
                .filter(asgard_db.ProcessRoutingGTI.processName == 'FIBREOPTIQUE') \
                .filter(asgard_db.ProcessRoutingGTI.id_statut == 3) \
                .filter(asgard_db.UsersRoutingGTI.id_users == user_id) \
                .order_by(asgard_db.ProcessPV.dateEntreeStation.desc())

            dashboard=[]
            
            for dash in qry.all():   
                dashboard.append({
                    u"id": dash.id,
                    u"PGM": dash.pgm,
                    u"MSN": dash.msn,
                    u"Gamme": dash.gamme,
                    u"CptGrGam": dash.cptGrGam,
                    u"Prépa SAP": "True" if dash.prepaSap==1 else "False",
                    u"Ordre de Fab": dash.ordreFabrication,
                    u"Prépa PV": "True" if dash.prepaPV==1 else "False",
                    u"Prépa PDF": "True" if dash.prepaPdf==1 else "False",
                    u"Maj SAP": "True" if dash.majSap==1 else "False",
                    u"Date Prépa SAP": dash.datePrepaSap if dash.datePrepaSap is None else dash.datePrepaSap.strftime('%Y-%m-%d %H:%M'),
                    u"Date Ajout OF": dash.dateAddOf if dash.dateAddOf is None else dash.dateAddOf.strftime('%Y-%m-%d %H:%M'),
                    u"Date Maj PV": dash.dateMajPV if dash.dateMajPV is None else dash.dateMajPV.strftime('%Y-%m-%d %H:%M'),
                    u"Date entrée station": dash.dateEntreeStation if dash.dateEntreeStation is None else dash.dateEntreeStation.strftime('%Y-%m-%d %H:%M'),
                    u"Statut": dash.statutScript,
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())



@web.route(u"/api/optique/dashboard-bdo")
class DashboardBdoHandler(web.handler.JsonHandler):
    class JsonDashboard(TypedDict):
        id: int
        pgm: str
        msn: int
        numRequestCirce: int
        dateRequestCirce: datetime.datetime
        loginCirceRequestor: str
        loginWindowsRequestor: str
        numCirceTreatment: str
        dateCirceTreatment: datetime.datetime
        dateRecupCirceTreatment: datetime.datetime

    def get(self):

        user_id = self.user[u"id"]

        out = web.handler.JsonResponse[DashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"OPTIQUE:DISPLAY")

        if out.ok() and user_id:

            qry = self.db_session.query(asgard_db.ProcessCirce) \
                .order_by(asgard_db.ProcessCirce.dateRequestCirce.desc())

            dashboard=[]
            
            for dash in qry.all():   
                dashboard.append({
                    u"id": dash.id,
                    u"pgm": dash.pgm,
                    u"msn": dash.msn,
                    u"numRequestCirce": dash.numRequestCirce,
                    u"dateRequestCirce": dash.dateRequestCirce if dash.dateRequestCirce is None else dash.dateRequestCirce.strftime('%Y-%m-%d %H:%M'),
                    u"loginCirceRequestor": dash.loginCirceRequestor,
                    u"loginWindowsRequestor": dash.loginWindowsRequestor,
                    u"numCirceTreatment": dash.numCirceTreatment,
                    u"dateCirceTreatment": dash.dateCirceTreatment if dash.dateCirceTreatment is None else dash.dateCirceTreatment.strftime('%Y-%m-%d %H:%M'),
                    u"dateRecupCirceTreatment": dash.dateRecupCirceTreatment if dash.dateRecupCirceTreatment is None else dash.dateRecupCirceTreatment.strftime('%Y-%m-%d %H:%M'),
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())

    def post(self):

        user_id = self.user[u"id"]

        out = web.handler.JsonResponse[DashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"OPTIQUE:DISPLAY")

        if out.ok() and user_id:

            qry = self.db_session.query(asgard_db.ProcessCirce) \
                .order_by(asgard_db.ProcessCirce.dateRequestCirce.desc())

            dashboard=[]
            
            for dash in qry.all():   
                dashboard.append({
                    u"id": dash.id,
                    u"pgm": dash.pgm,
                    u"msn": dash.msn,
                    u"numRequestCirce": dash.numRequestCirce,
                    u"dateRequestCirce": dash.dateRequestCirce if dash.dateRequestCirce is None else dash.dateRequestCirce.strftime('%Y-%m-%d %H:%M'),
                    u"loginCirceRequestor": dash.loginCirceRequestor,
                    u"loginWindowsRequestor": dash.loginWindowsRequestor,
                    u"numCirceTreatment": dash.numCirceTreatment,
                    u"dateCirceTreatment": dash.dateCirceTreatment if dash.dateCirceTreatment is None else dash.dateCirceTreatment.strftime('%Y-%m-%d %H:%M'),
                    u"dateRecupCirceTreatment": dash.dateRecupCirceTreatment if dash.dateRecupCirceTreatment is None else dash.dateRecupCirceTreatment.strftime('%Y-%m-%d %H:%M'),
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())