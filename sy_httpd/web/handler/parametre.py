from typing import Any, Dict, List, Optional, Tuple
from mypy_extensions import TypedDict
from datetime import datetime
from sqlalchemy import true
from sqlalchemy import delete
import web.handler
import saga_db
import config
from sqlalchemy import func, true
from sqlalchemy import literal_column

## APPLICATION ##

@web.route("/api/param/Role")
class RoleHandler(web.handler.JsonHandler):
    def post(self) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.Role).order_by(saga_db.Role.nom)

            tab=[]
            for res in qry.all():  
                tab.append({
                    "id": res.id,
                    "nom": res.nom,
                    "description": res.description,
                })

            out.set_body(tab)

        self.write_json(out.to_dict())

@web.route("/api/param/Autorisation")
class RoleHandler(web.handler.JsonHandler):
    def post(self) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.Autorisation).order_by(saga_db.Autorisation.nom)

            tab=[]
            for res in qry.all():  
                tab.append({
                    "id": res.id,
                    "text": res.nom,
                    "nom": res.nom,
                    "description": res.description,
                })

            out.set_body(tab)

        self.write_json(out.to_dict())

@web.route("/api/param/role-autorisation")
class RoleAutorisationHandler(web.handler.JsonHandler):
    def get(self) -> None:

        user_id = self.user["id"]

        authorization = "ROLE_AUTORISATION:DISPLAY"

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.RoleAutorisation).order_by(saga_db.RoleAutorisation.id_role)

            tabRole=[]
            tabAut = []
            tabIdAut = []
            id_role_inc = 0
            count = 0

            for res in qry.all():
                count = count + 1

                if id_role_inc != 0 and id_role_inc!=res.id_role:
                    tabRole.append({
                        "id_role": id_role,
                        "nom_role": role,
                        "desc_role": res.role.description,
                        "auth": tabAut,
                        "tabIdAut": tabIdAut,
                    })
                    tabAut = []
                    tabIdAut = []

                tabAut.append({
                    "id_aut": res.id_autorisation,
                    "nom_aut": res.autorisation.nom,
                    "desc_aut": res.autorisation.description,
                })
                tabIdAut.append(res.id_autorisation)
                id_role = res.id_role
                role = res.role.nom
                id_role_inc = id_role

            if count > 0:
                tabRole.append({
                    "id_role": id_role,
                    "nom_role": role,
                    "desc_role": res.role.description,
                    "auth": tabAut,
                    "tabIdAut": tabIdAut,
                })
            

            out.set_body(tabRole)

        self.write_json(out.to_dict())

@web.route("/api/param/role-autorisation/edit")
class RoleAutorisationEditHandler(web.handler.JsonHandler):

    def post(self) -> None:
        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        id_role = params.get("id_role", 0)
        tab_id_Aut = params.get("value", [])
        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            # Suppression de toutes les autorisations ayant le role demandé
            self.db_session.query(saga_db.RoleAutorisation).filter_by(id_role=id_role).delete()
            self.db_session.commit()

            for v in tab_id_Aut:
                id_autorisation = v

                # Ajout des nouvelles autorisations passées en paramètre
                db_add = saga_db.RoleAutorisation()
                db_add.id_role = id_role
                db_add.id_autorisation = id_autorisation
                self.db_session.add(db_add)
                self.db_session.commit()

            out.set_body("Valeur mis à jour dans la table RoleAutorisation")
        
        self.write_json(out.to_dict())

@web.route("/api/param/version")
class VersionHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():
            """
            qry = self.db_session.query(saga_db.Version) \
                .filter(saga_db.Version.target == target) \
                .order_by(saga_db.Version.date)
            """
            if config.FRONTEND_URL == "http://localhost":
                qry = self.db_session.query(saga_db.Version) \
                        .order_by(saga_db.Version.version)
            else:
                qry = self.db_session.query(saga_db.Version) \
                        .filter(saga_db.Version.target == "PROD") \
                        .order_by(saga_db.Version.version)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "version": param.version,
                    "target": param.target,
                    "date": param.date.strftime('%Y-%m-%d') if param.date != None else str(datetime.now().strftime('%Y-%m-%d')) ,
                    "description": param.description,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/Version/add")
class VersionAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Version()
            db_param.version = addRow["version"] if "version" in addRow else ""
            db_param.target = addRow["target"] if "target" in addRow else ""
            db_param.date = addRow["date"] if "date" in addRow else datetime.now().strftime('%Y-%m-%d')
            db_param.description = addRow["description"] if "description" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Version")

        self.write_json(out.to_dict())

@web.route("/api/param/Role/add")
class RoleAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Role()

            db_param.nom = addRow["nom"] if "nom" in addRow else ""
            db_param.description = addRow["description"] if "description" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Role")

        self.write_json(out.to_dict())

@web.route("/api/param/Autorisation/add")
class AutorisationAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Autorisation()

            db_param.nom = addRow["nom"] if "nom" in addRow else ""
            db_param.description = addRow["description"] if "description" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Autorisation")

        self.write_json(out.to_dict())

@web.route("/api/param/:tableParam/edit")
class ParamEditHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        if tableParam == "Role":
            tableParamObj = saga_db.Role       
        elif tableParam == "Autorisation":
            tableParamObj = saga_db.Autorisation   
        elif tableParam == "version":
            tableParamObj = saga_db.Version           

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            for v in saveRows:
                rowId = v["id"]
                columnName = v['columnName']
                value = v['value']
                colId = "id"

                param = self.db_session.query(tableParamObj).get({colId:rowId})
                setattr(param, columnName, value)
                self.db_session.commit()

            out.set_body("Valeur enregistrée dans la table " + tableParam)

        self.write_json(out.to_dict())

@web.route("/api/param/:tableParam/del")
class ParamDelHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        rowId = params.get("RowsId", "")

        if tableParam == "Role":
            tableParamObj = saga_db.Role       
        elif tableParam == "Autorisation":
            tableParamObj = saga_db.Autorisation    
        elif tableParam == "version":
            tableParamObj = saga_db.Version  

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:
            
            # Sélection de la ligne ID à supprimer
            param = self.db_session.query(tableParamObj).filter_by(id=rowId).first()

            # Suppression de la ligne
            self.db_session.delete(param)

            # Confirmer la suppression
            self.db_session.commit()

            if tableParam == "Role": 
                self.delRoleUser(rowId)
                self.delRoleAutorisation(rowId)

            out.set_body("Id " + str(rowId) + " supprimé dans la table " + tableParam)

        self.write_json(out.to_dict())
    

    def delRoleUser(self, rowId):
        # Nouvelle syntaxe cf doc SqlAlchemy
        statement = delete(saga_db.UtilisateurRole).where(saga_db.UtilisateurRole.id_role==rowId)
        self.db_session.execute(statement)
        self.db_session.commit()

    def delRoleAutorisation(self, rowId):
        # Nouvelle syntaxe cf doc SqlAlchemy
        statement = delete(saga_db.RoleAutorisation).where(saga_db.RoleAutorisation.id_role==rowId)
        self.db_session.execute(statement)
        self.db_session.commit()


## Bibliothèque ##

@web.route("/api/bibliotheque/param/saga")
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
                    "name_saga": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/auteur")
class BibliothequeAuteurHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_Auteur.id, saga_db.Bibliotheque_Auteur.name_author, func.string_agg(saga_db.Bibliotheque_Job.name_job, literal_column("', '")).label('name_job'),) \
                                    .outerjoin(saga_db.Bibliotheque_JobAuteur, saga_db.Bibliotheque_JobAuteur.id_author == saga_db.Bibliotheque_Auteur.id) \
                                    .outerjoin(saga_db.Bibliotheque_Job, saga_db.Bibliotheque_JobAuteur.id_job == saga_db.Bibliotheque_Job.id) \
                                    .group_by(saga_db.Bibliotheque_Auteur.id, saga_db.Bibliotheque_Auteur.name_author) \
                                    .distinct()

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "name_author": param.name_author,
                    "name_job": param.name_job,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/job")
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
                    "name_job": param.name_job,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/categorie")
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
                    "name_categorie": param.name_categorie,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/bookpublishing")
class BibliothequeBookPublishingHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bibliotheque_MaisonEdition) \
                .order_by(saga_db.Bibliotheque_MaisonEdition.name_book_publishing)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "name_book_publishing": param.name_book_publishing,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/owner")
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
                    "name_owner": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/location")
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
                    "name_location": param.name_location,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/saga/add")
class BibliothequeSagaAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_Saga()
            db_param.name_saga = addRow["name_saga"] if "name_saga" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Saga")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/auteur/add")
class BibliothequeAuteurAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_Auteur()
            db_param.name_author = addRow["name_author"] if "name_author" in addRow else ""
            self.db_session.add(db_param)
            self.db_session.flush()
            # At this point, the object db_Bib has been pushed to the DB, 
            # and has been automatically assigned a unique primary key id
            self.db_session.refresh(db_param)
            # refresh updates given object in the session with its state in the DB
            id_author = db_param.id
            # is the automatically assigned primary key ID given in the database.
            self.db_session.commit()

            for id_job in addRow["name_job"]:
                db_jobAuteur = saga_db.Bibliotheque_JobAuteur()
                db_jobAuteur.id_job = id_job
                db_jobAuteur.id_author = id_author
                self.db_session.add(db_jobAuteur)
                self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Auteur et AuteurJob")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/categorie/add")
class BibliothequeCategorieAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_Categorie()
            db_param.name_categorie = addRow["name_categorie"] if "name_categorie" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bibliotheque_categorie")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/bookpublishing/add")
class BibliothequeBookPublishingAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_MaisonEdition()
            db_param.name_book_publishing = addRow["name_book_publishing"] if "name_book_publishing" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table book_publishing")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/owner/add")
class BibliothequeOwnerAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_Proprietaire()
            db_param.name_owner = addRow["name_owner"] if "name_owner" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table owner")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/location/add")
class BibliothequeLocationAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bibliotheque_Emplacement()
            db_param.name_location = addRow["name_location"] if "name_location" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table location")

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/:tableParam/edit")
class BibliothequeParamEditHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        if tableParam == "saga":
            tableParamObj = saga_db.Bibliotheque_Saga        
        elif tableParam == "auteur":
            tableParamObj = saga_db.Bibliotheque_Auteur  
        elif tableParam == "categorie":
            tableParamObj = saga_db.Bibliotheque_Categorie 
        elif tableParam == "bookpublishing":
            tableParamObj = saga_db.Bibliotheque_MaisonEdition
        elif tableParam == "owner":
            tableParamObj = saga_db.Bibliotheque_Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Bibliotheque_Emplacement

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            for v in saveRows:
                rowId = v["id"]
                columnName = v['columnName']
                value = v['value']
                colId = "id"
                
                if tableParam == "auteur" and columnName=="name_job":
                    # Suppression dans la table de lien entre Métier et auteurs
                    param = self.db_session.query(saga_db.Bibliotheque_JobAuteur).filter_by(id_author=rowId).delete()
                    self.db_session.commit()

                    # Ajout des nouveaux éléments
                    for id_job in value:
                        db_jobAuteur = saga_db.Bibliotheque_JobAuteur()
                        db_jobAuteur.id_job = id_job
                        db_jobAuteur.id_author = rowId
                        self.db_session.add(db_jobAuteur)
                        self.db_session.commit()
                else:
                    param = self.db_session.query(tableParamObj).get({colId:rowId})
                    setattr(param, columnName, value)
                    self.db_session.commit()

            out.set_body("Valeur enregistrée dans la table " + tableParam)

        self.write_json(out.to_dict())

@web.route("/api/bibliotheque/param/:tableParam/del")
class BibliothequeParamDelHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        rowId = params.get("RowsId", "")

        if tableParam == "saga":
            tableParamObj = saga_db.Bibliotheque_Saga
        elif tableParam == "auteur":
            tableParamObj = saga_db.Bibliotheque_Auteur  
        elif tableParam == "categorie":
            tableParamObj = saga_db.Bibliotheque_Categorie 
        elif tableParam == "bookpublishing":
            tableParamObj = saga_db.Bibliotheque_MaisonEdition
        elif tableParam == "owner":
            tableParamObj = saga_db.Bibliotheque_Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Bibliotheque_Emplacement

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:
            
            # Sélection de la ligne ID à supprimer
            param = self.db_session.query(tableParamObj).filter_by(id=rowId).first()

            # Suppression de la ligne
            self.db_session.delete(param)

            # Confirmer la suppression
            self.db_session.commit()

            if tableParam == "auteur":
                # Suppression dans la table de lien entre Métier et auteurs
                param = self.db_session.query(saga_db.Bibliotheque_JobAuteur).filter_by(id_author=rowId).delete()
                self.db_session.commit()

            out.set_body("Id " + str(rowId) + " supprimé dans la table " + tableParam)

        self.write_json(out.to_dict())


## BLURAY ##

@web.route("/api/bluray/param/saga")
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
                    "name_saga": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/coffret")
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
                    "name_coffret": param.name_coffret,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/categorie")
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
                    "name_categorie": param.name_categorie,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/owner")
class BlurayOwnerHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Bluray_Proprietaire) \
                .order_by(saga_db.Bluray_Proprietaire.name_owner)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "name_owner": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/location")
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
                    "name_location": param.name_location,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/saga/add")
class BluraySagaAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bluray_Saga()
            db_param.name_saga = addRow["name_saga"] if "name_saga" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray_Saga")

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/coffret/add")
class BlurayCoffretAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bluray_Coffret()
            db_param.name_author = addRow["name_coffret"] if "name_coffret" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray_Coffret")

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/categorie/add")
class BlurayCategorieAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bluray_Categorie()
            db_param.name_categorie = addRow["name_categorie"] if "name_categorie" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray_Categorie")

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/owner/add")
class BlurayOwnerAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bluray_Proprietaire()
            db_param.name_owner = addRow["name_owner"] if "name_owner" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray_Proprietaire")

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/location/add")
class BlurayLocationAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Bluray_Emplacement()
            db_param.name_location = addRow["name_location"] if "name_location" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Bluray_Emplacement")

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/:tableParam/edit")
class BlurayParamEditHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        if tableParam == "saga":
            tableParamObj = saga_db.Bluray_Saga        
        elif tableParam == "coffret":
            tableParamObj = saga_db.Bluray_Coffret  
        elif tableParam == "categorie":
            tableParamObj = saga_db.Bluray_Categorie 
        elif tableParam == "owner":
            tableParamObj = saga_db.Bluray_Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Bluray_Emplacement

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            for v in saveRows:
                rowId = v["id"]
                columnName = v['columnName']
                value = v['value']
                colId = "id"

                param = self.db_session.query(tableParamObj).get({colId:rowId})
                setattr(param, columnName, value)
                self.db_session.commit()

            out.set_body("Valeur enregistrée dans la table " + tableParam)

        self.write_json(out.to_dict())

@web.route("/api/bluray/param/:tableParam/del")
class BlurayParamDelHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        rowId = params.get("RowsId", "")

        if tableParam == "saga":
            tableParamObj = saga_db.Bluray_Saga
        elif tableParam == "coffret":
            tableParamObj = saga_db.Bluray_Coffret  
        elif tableParam == "categorie":
            tableParamObj = saga_db.Bluray_Categorie 
        elif tableParam == "bookpublishing":
            tableParamObj = saga_db.Bluray_MaisonEdition
        elif tableParam == "owner":
            tableParamObj = saga_db.Bluray_Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Bluray_Emplacement

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:
            
            # Sélection de la ligne ID à supprimer
            param = self.db_session.query(tableParamObj).filter_by(id=rowId).first()

            # Suppression de la ligne
            self.db_session.delete(param)

            # Confirmer la suppression
            self.db_session.commit()

            out.set_body("Id " + str(rowId) + " supprimé dans la table " + tableParam)

        self.write_json(out.to_dict())

