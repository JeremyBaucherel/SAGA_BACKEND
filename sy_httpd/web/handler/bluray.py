from asyncio.windows_events import NULL
from typing import Any, Dict, List, Optional, Tuple
from xmlrpc.client import boolean
from mypy_extensions import TypedDict
import hashlib
import random
import sendmail
import string
from sqlalchemy import func, true
from sqlalchemy import null
from sqlalchemy import literal_column
import tornado
import uuid
import datetime
import config
import web.handler
import saga_db

@web.route(u"/api/bluray/dashboard")
class BlurayDashboardHandler(web.handler.JsonHandler):
    class JsonDashboard(TypedDict):
        id: int
        titre: str
        id_categorie: int
        name_categorie: str
        id_saga: int
        name_saga: str
        number: str
        steelbook: int
        id_coffret: int
        name_coffret: str
        id_owner: int
        name_owner: str
        id_location: int
        name_location: str

    def get(self):

        user_id = self.user[u"id"]

        out = web.handler.JsonResponse[BlurayDashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"BLURAY_DASHBOARD:DISPLAY")

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.Bluray
                                    ).outerjoin(saga_db.Bluray_Categorie) \
                                    .outerjoin(saga_db.Bluray_Emplacement) \
                                    .outerjoin(saga_db.Bluray_Proprietaire) \
                                    .outerjoin(saga_db.Bluray_Saga) \
                                    .outerjoin(saga_db.Bluray_Coffret) \
                                    .outerjoin(saga_db.Bluray_Emprunteur)

            dashboard=[]
            for dash in qry.all(): 
                dashboard.append({
                    u"id": dash.id, 
                    u"titre": dash.titre if dash.titre else "",
                    u"id_categorie": dash.id_categorie if dash.id_categorie else -1,
                    u"name_categorie": dash.Bluray_Categorie.name_categorie if dash.Bluray_Categorie else "",
                    u"id_saga": dash.id_saga if dash.id_saga else -1,
                    u"name_saga": dash.Bluray_Saga.name_saga if dash.Bluray_Saga else "",
                    u"number": dash.number if dash.number else "",
                    u"steelbook": dash.steelbook if dash.steelbook else "",
                    u"id_coffret": dash.id_coffret if dash.id_coffret else -1,
                    u"name_coffret": dash.Bluray_Coffret.name_coffret if dash.Bluray_Coffret else "",
                    u"id_owner": dash.id_owner if dash.id_owner else -1,
                    u"name_owner": dash.Bluray_Proprietaire.name_owner if dash.Bluray_Proprietaire else "",
                    u"id_location": dash.id_location if dash.id_location else -1,
                    u"name_location": dash.Bluray_Emplacement.name_location if dash.Bluray_Emplacement else "",
                    u"borrower": dash.Bluray_Emprunteur.borrower if dash.Bluray_Emprunteur else "",
                    u"borrowing_date": dash.Bluray_Emprunteur.borrowing_date.strftime('%Y-%m-%d %H:%M') if dash.Bluray_Emprunteur else "",
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())

@web.route(u"/api/bluray/dashboard/valretour")
class BlurayDashboardReturnBookHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        rowId = params.get("rowId", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            # Sélection de la ligne ID à supprimer
            param = self.db_session.query(saga_db.Bluray_Emprunteur).filter_by(id_bluray=rowId).first()
            # Suppression de la ligne
            self.db_session.delete(param)
            # Confirmer la suppression
            self.db_session.commit()

@web.route(u"/api/bluray/dashboard/edit")
class BlurayDashboardEditHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:
            ajout_emprunteur = False
            borrowing_date = datetime.datetime.now().strftime('%Y-%m-%d')
            borrower = ""

            for v in saveRows:
                edit = True
                rowId = v["id"]
                columnName = v['columnName']
                value = v['value'] if 'value' in v else None # Si on ne coche pas le menu déroulant la clef value n'existe plus, la valeur est alors défifine à NULL dans la BDD
                colId = "id"

                if columnName=="borrower" or columnName=="borrowing_date":
                    edit = False
                    param = self.db_session.query(saga_db.Bluray_Emprunteur).filter_by(id_bluray=rowId)

                    if param.count() > 0:

                        param = self.db_session.query(saga_db.Bluray_Emprunteur).filter(saga_db.Bluray_Emprunteur.id_bluray == rowId).first()

                        if columnName == "borrowing_date": 
                            value = datetime.datetime.strptime(value, '%Y-%m-%d')
                            param.borrowing_date = value
                        if columnName == "borrower":
                            param.borrower = value
                            
                        self.db_session.commit()
                    else:
                        ajout_emprunteur = True
                        if columnName == "borrower": borrower = value
                        if columnName == "borrowing_date": borrowing_date = datetime.datetime.strptime(value, '%Y-%m-%d')

                if edit:
                    # Dans le cas ou la valeur provient d'une liste avec un seul item posible on récupère l'indice 0
                    if columnName in ["name_categorie", "name_saga", "name_coffret", "name_owner", "name_location"]:
                        if len(value)>0:
                            value = value[0]
                        else:
                            value = None

                    # Le nom de la colonne name_ est remplacé par id_
                    columnName = columnName.replace("name_", "id_")

                    # Dans le cas ou la valeur provient d'une liste avec plusieurs items posible on boucle sur les indices
                    param = self.db_session.query(saga_db.Bluray).get({colId:rowId})
                    setattr(param, columnName, value)
                    self.db_session.commit()

            if ajout_emprunteur:
                db_Emp = saga_db.Bluray_Emprunteur()
                db_Emp.id_bluray = rowId
                db_Emp.borrower = borrower
                db_Emp.borrowing_date = borrowing_date
                self.db_session.add(db_Emp)
                self.db_session.commit()


            out.set_body("Valeur enregistrée dans la table Bluray")

        self.write_json(out.to_dict())

@web.route(u"/api/bluray/dashboard/add")
class BlurayDashboardAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            id_categorie = addRow["name_categorie"][0] if "name_categorie" in addRow and addRow["name_categorie"] != None else None
            id_saga = addRow["name_saga"][0] if "name_saga" in addRow and addRow["name_saga"] != None else None
            id_coffret = addRow["name_coffret"][0] if "name_coffret" in addRow and addRow["name_coffret"] != None else None
            id_owner = addRow["name_owner"][0] if "name_owner" in addRow and addRow["name_owner"] != None else None
            id_location = addRow["name_location"][0] if "name_location" in addRow and addRow["name_location"] != None else None
            
            db_Bib = saga_db.Bluray()
            db_Bib.titre = addRow["titre"] if "titre" in addRow else ""
            db_Bib.id_categorie = id_categorie
            db_Bib.id_saga = id_saga
            db_Bib.number = addRow["number"] if "number" in addRow else ""
            db_Bib.steelbook = addRow["steelbook"] if "steelbook" in addRow else 0
            db_Bib.id_coffret = id_coffret
            db_Bib.id_owner = id_owner
            db_Bib.id_location = id_location
            self.db_session.add(db_Bib)
            self.db_session.flush()
            # At this point, the object db_Bib has been pushed to the DB, 
            # and has been automatically assigned a unique primary key id
            self.db_session.refresh(db_Bib)
            # refresh updates given object in the session with its state in the DB

            id_bluray = db_Bib.id
            # is the automatically assigned primary key ID given in the database.
            self.db_session.commit()

            if "borrower" in addRow and "borrowing_date" in addRow:
                db_Emp = saga_db.Bluray_Emprunteur()
                db_Emp.id_bluray = id_bluray
                db_Emp.borrower = addRow["borrower"] if "borrower" in addRow else ""
                db_Emp.borrowing_date = datetime.datetime.strptime(addRow["borrowing_date"], '%Y-%m-%d') if "borrowing_date" in addRow else datetime.datetime.now().strftime('%Y-%m-%d')
                self.db_session.add(db_Emp)

                self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray")

@web.route(u"/api/bluray/dashboard/del")
class BlurayDashboardDelHandler(web.handler.JsonHandler):

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
            param = self.db_session.query(saga_db.Bluray).filter_by(id=delRow).first()
            # Suppression de la ligne
            self.db_session.delete(param)
            # Confirmer la suppression
            self.db_session.commit()

            # Suppression dans la table Bluray_Emprunteur
            borrower = self.db_session.query(saga_db.Bluray_Emprunteur).filter_by(id_bluray=delRow).first()
            if not borrower is None:
                self.db_session.delete(borrower)
                self.db_session.commit()     

@web.route("/api/bluray/liste/saga")
class BluraySagaHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Saga) \
                .order_by(saga_db.Bluray_Saga.name_saga)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/liste/owner")
class BlurayqueOwnerHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Proprietaire) \
                .order_by(saga_db.Bluray_Proprietaire.name_owner)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/liste/location")
class BlurayLocationHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Emplacement) \
                .order_by(saga_db.Bluray_Emplacement.name_location)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_location,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/liste/categorie")
class BlurayCategorieHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Categorie) \
                .order_by(saga_db.Bluray_Categorie.name_categorie)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_categorie,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/liste/coffret")
class BlurayCoffretHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Coffret) \
                .order_by(saga_db.Bluray_Coffret.name_coffret)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_coffret,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

