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

@web.route(u"/api/bibliotheque/dashboard")
class BibliothequeDashboardHandler(web.handler.JsonHandler):
    class JsonDashboard(TypedDict):
        id: int
        id_categorie: int
        name_categorie: str
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

        out = web.handler.JsonResponse[BibliothequeDashboardHandler.JsonDashboard]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"BOOK_DASHBOARD:DISPLAY")

        if out.ok() and user_id:
            """
            qry = self.db_session.query(saga_db.Bibliotheque) \
                .outerjoin(saga_db.Bibliotheque_Categorie) \
                .outerjoin(saga_db.Bibliotheque_Emplacement) \
                .outerjoin(saga_db.Bibliotheque_Proprietaire) \
                .outerjoin(saga_db.Bibliotheque_) \
                .outerjoin(saga_db.Bibliotheque_MaisonEdition)
            """
            qry = self.db_session.query(saga_db.Bibliotheque.id,
                                        saga_db.Bibliotheque.id_categorie,
                                        saga_db.Bibliotheque_Categorie.name_categorie,
                                        saga_db.Bibliotheque.id_saga,
                                        saga_db.Bibliotheque_Saga.name_saga,
                                        saga_db.Bibliotheque.number,
                                        saga_db.Bibliotheque.name,
                                        saga_db.Bibliotheque.id_book_publishing,
                                        saga_db.Bibliotheque_MaisonEdition.name_book_publishing,
                                        saga_db.Bibliotheque.id_owner,
                                        saga_db.Bibliotheque_Proprietaire.name_owner,
                                        saga_db.Bibliotheque.id_location,
                                        saga_db.Bibliotheque_Emplacement.name_location,
                                        func.string_agg(saga_db.Bibliotheque_Auteur.name_author, literal_column("', '")).label('name_author'),
                                        saga_db.Bibliotheque_Emprunteur.borrower,
                                        saga_db.Bibliotheque_Emprunteur.borrowing_date
                                    ).outerjoin(saga_db.Bibliotheque_Categorie) \
                                    .outerjoin(saga_db.Bibliotheque_Emplacement) \
                                    .outerjoin(saga_db.Bibliotheque_Proprietaire) \
                                    .outerjoin(saga_db.Bibliotheque_Saga) \
                                    .outerjoin(saga_db.Bibliotheque_MaisonEdition) \
                                    .outerjoin(saga_db.Bibliotheque_Emprunteur) \
                                        .outerjoin(saga_db.Bibliotheque_AuteurBibliotheque) \
                                        .outerjoin(saga_db.Bibliotheque_Auteur) \
                                    .group_by(saga_db.Bibliotheque.id,
                                        saga_db.Bibliotheque.id_categorie,
                                        saga_db.Bibliotheque_Categorie.name_categorie,
                                        saga_db.Bibliotheque.id_saga,
                                        saga_db.Bibliotheque_Saga.name_saga,
                                        saga_db.Bibliotheque.number,
                                        saga_db.Bibliotheque.name,
                                        saga_db.Bibliotheque.id_book_publishing,
                                        saga_db.Bibliotheque_MaisonEdition.name_book_publishing,
                                        saga_db.Bibliotheque.id_owner,
                                        saga_db.Bibliotheque_Proprietaire.name_owner,
                                        saga_db.Bibliotheque.id_location,
                                        saga_db.Bibliotheque_Emplacement.name_location,
                                        saga_db.Bibliotheque_Emprunteur.borrower,
                                        saga_db.Bibliotheque_Emprunteur.borrowing_date,
                                        saga_db.Bibliotheque_AuteurBibliotheque.id_book_list) \
                                    .distinct()

            dashboard=[]
            
            for dash in qry.all(): 
                dashboard.append({
                    u"id": dash.id,
                    u"id_categorie": dash.id_categorie,
                    u"name_categorie": dash.name_categorie,
                    u"id_saga": dash.id_saga if dash.id_saga else -1,
                    u"name_saga": dash.name_saga if dash.name_saga else "",
                    u"number": dash.number,
                    u"name": dash.name,
                    u"id_book_publishing": dash.id_book_publishing if dash.id_book_publishing else -1,
                    u"name_book_publishing": dash.name_book_publishing if dash.name_book_publishing else "",
                    u"id_owner": dash.id_owner if dash.id_owner else -1,
                    u"name_owner": dash.name_owner if dash.name_owner else "",
                    u"id_location": dash.id_location if dash.id_location else -1,
                    u"name_location": dash.name_location if dash.name_location else "",
                    u"authors": dash.name_author if dash.name_author else "",
                    u"borrower": dash.borrower if dash.borrower else "",
                    u"borrowing_date": dash.borrowing_date.strftime('%Y-%m-%d %H:%M') if dash.borrowing_date else "",
                })
            #dashboard = sorted(dashboard, key=lambda x: x[u"Date entrée station"])
            out.set_body(dashboard)

        self.write_json(out.to_dict())

@web.route(u"/api/bibliotheque/dashboard/valretour")
class BlibliothequeDashboardReturnBookHandler(web.handler.JsonHandler):

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
            param = self.db_session.query(saga_db.Bibliotheque_Emprunteur).filter_by(id_book_list=rowId).first()
            # Suppression de la ligne
            self.db_session.delete(param)
            # Confirmer la suppression
            self.db_session.commit()

@web.route(u"/api/bibliotheque/dashboard/edit")
class BibliothequeDashboardEditHandler(web.handler.JsonHandler):

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

                # Le nom de la colonne name_ est remplacé par id_
                columnName = columnName.replace("name_", "id_")

                if columnName=="borrower" or columnName=="borrowing_date":
                    edit = False
                    param = self.db_session.query(saga_db.Bibliotheque_Emprunteur).filter_by(id_book_list=rowId)

                    if param.count() > 0:

                        param = self.db_session.query(saga_db.Bibliotheque_Emprunteur).filter(saga_db.Bibliotheque_Emprunteur.id_book_list == rowId).first()

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

                if columnName == "authors":
                    edit = False
                    # Suppression dans la table de lien entre Métier et auteurs
                    param = self.db_session.query(saga_db.Bibliotheque_AuteurBibliotheque).filter_by(id_book_list=rowId).delete()
                    self.db_session.commit()

                    # Ajout des nouveaux éléments
                    for id_auteur in value:
                        db_bookAuteur = saga_db.Bibliotheque_AuteurBibliotheque()
                        db_bookAuteur.id_book_list = rowId
                        db_bookAuteur.id_author = id_auteur
                        self.db_session.add(db_bookAuteur)
                        self.db_session.commit()

                if edit:
                    # Dans le cas ou la valeur provient d'une liste avec un seul item posible on récupère l'indice 0
                    if columnName in ["name_categorie", "name_saga", "name_book_publishing", "name_owner", "name_location"] and value!= None:
                        value = value[0]

                    # Dans le cas ou la valeur provient d'une liste avec plusieurs items posible on boucle sur les indices
                    param = self.db_session.query(saga_db.Bibliotheque).get({colId:rowId})
                    setattr(param, columnName, value)
                    self.db_session.commit()

            if ajout_emprunteur:
                db_Emp = saga_db.Bibliotheque_Emprunteur()
                db_Emp.id_book_list = rowId
                db_Emp.borrower = borrower
                db_Emp.borrowing_date = borrowing_date
                self.db_session.add(db_Emp)
                self.db_session.commit()


            out.set_body("Valeur enregistrée dans la table Bibliotheque")

        self.write_json(out.to_dict())

@web.route(u"/api/bibliotheque/dashboard/add")
class BibliothequeDashboardAddHandler(web.handler.JsonHandler):

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
            id_book_publishing = addRow["name_book_publishing"][0] if "name_book_publishing" in addRow and addRow["name_book_publishing"] != None else None
            id_owner = addRow["name_owner"][0] if "name_owner" in addRow and addRow["name_owner"] != None else None
            id_location = addRow["name_location"][0] if "name_location" in addRow and addRow["name_location"] != None else None
            
            db_Bib = saga_db.Bibliotheque()
            db_Bib.id_categorie = id_categorie
            db_Bib.id_saga = id_saga
            db_Bib.number = addRow["number"] if "number" in addRow else ""
            db_Bib.name = addRow["name"] if "name" in addRow else ""
            db_Bib.id_book_publishing = id_book_publishing
            db_Bib.id_owner = id_owner
            db_Bib.id_location = id_location
            self.db_session.add(db_Bib)
            self.db_session.flush()
            # At this point, the object db_Bib has been pushed to the DB, 
            # and has been automatically assigned a unique primary key id
            self.db_session.refresh(db_Bib)
            # refresh updates given object in the session with its state in the DB

            id_book_list = db_Bib.id
            # is the automatically assigned primary key ID given in the database.
            self.db_session.commit()

            if "borrower" in addRow and "borrowing_date" in addRow:
                db_Emp = saga_db.Bibliotheque_Emprunteur()
                db_Emp.id_book_list = id_book_list
                db_Emp.borrower = addRow["borrower"] if "borrower" in addRow else ""
                db_Emp.borrowing_date = datetime.datetime.strptime(addRow["borrowing_date"], '%Y-%m-%d') if "borrowing_date" in addRow else datetime.datetime.now().strftime('%Y-%m-%d')
                self.db_session.add(db_Emp)

                self.db_session.commit()

            if "authors" in addRow and addRow["authors"] != None:   
                # Ajout des nouveaux éléments
                for id_auteur in addRow["authors"]:
                    db_bookAuteur = saga_db.Bibliotheque_AuteurBibliotheque()
                    db_bookAuteur.id_book_list = id_book_list
                    db_bookAuteur.id_author = id_auteur
                    self.db_session.add(db_bookAuteur)
                    self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bibliotheque")

@web.route(u"/api/bibliotheque/dashboard/del")
class BibliothequeDashboardDelHandler(web.handler.JsonHandler):

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
            param = self.db_session.query(saga_db.Bibliotheque).filter_by(id=delRow).first()
            # Suppression de la ligne
            self.db_session.delete(param)
            # Confirmer la suppression
            self.db_session.commit()

            # Suppression dans la table Bibliotheque_Emprunteur
            borrower = self.db_session.query(saga_db.Bibliotheque_Emprunteur).filter_by(id_book_list=delRow).first()
            if not borrower is None:
                self.db_session.delete(borrower)
                self.db_session.commit()

            # Suppression dans la table Author_book_list
            authorBookList = self.db_session.query(saga_db.Bibliotheque_AuteurBibliotheque).filter_by(id_book_list=delRow).first()
            if not authorBookList is None:
                self.db_session.delete(authorBookList)
                self.db_session.commit()           

@web.route("/api/bibliotheque/liste/categorie")
class BibliothequeCategorieHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Categorie) \
                .order_by(saga_db.Bibliotheque_Categorie.name_categorie)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_categorie,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/job")
class BibliothequeJobHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Job) \
                .order_by(saga_db.Bibliotheque_Job.name_job)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_job,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/saga")
class BibliothequeSagaHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Saga) \
                .order_by(saga_db.Bibliotheque_Saga.name_saga)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/publishing")
class BibliothequePublishingHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_MaisonEdition) \
                .order_by(saga_db.Bibliotheque_MaisonEdition.name_book_publishing)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_book_publishing,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/owner")
class BibliothequeOwnerHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Proprietaire) \
                .order_by(saga_db.Bibliotheque_Proprietaire.name_owner)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/location")
class BibliothequeLocationHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Emplacement) \
                .order_by(saga_db.Bibliotheque_Emplacement.name_location)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_location,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/liste/author")
class BibliothequeAuthorHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Auteur) \
                .order_by(saga_db.Bibliotheque_Auteur.name_author)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "text": param.name_author,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())
