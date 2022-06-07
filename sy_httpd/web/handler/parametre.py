from typing import Any, Dict, List, Optional, Tuple
from mypy_extensions import TypedDict
from datetime import datetime
from sqlalchemy import true
from sqlalchemy import delete
import web.handler
import saga_db
import config


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

# Utilisation pour la page d'administration des rôles et autorisations (FormList)
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
class ParamEditHandler(web.handler.JsonHandler):

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

@web.route("/api/param/saga")
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
                    "name_saga": param.name_saga,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/auteur")
class AuteurHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.Auteur) \
                .order_by(saga_db.Auteur.name_author)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "name_author": param.name_author,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/type")
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
                    "name_type": param.name_type,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/bookpublishing")
class BookPublishingHandler(web.handler.JsonHandler):
    def post(self):

        out = web.handler.JsonResponse()

        if out.ok():

            qry = self.db_session.query(saga_db.MaisonEdition) \
                .order_by(saga_db.MaisonEdition.name_book_publishing)

            tabParam=[]
            for param in qry.all():  
                tabParam.append({
                    "id": param.id,
                    "name_book_publishing": param.name_book_publishing,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/owner")
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
                    "name_owner": param.name_owner,
                })

            out.set_body(tabParam)

        self.write_json(out.to_dict())

@web.route("/api/param/location")
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
                    "name_location": param.name_location,
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

@web.route("/api/param/saga/add")
class SagaAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Saga()
            db_param.name_saga = addRow["name_saga"] if "name_saga" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Saga")

        self.write_json(out.to_dict())

@web.route("/api/param/auteur/add")
class AuteurAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Auteur()
            db_param.name_author = addRow["name_author"] if "name_author" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Auteur")

        self.write_json(out.to_dict())

@web.route("/api/param/type/add")
class TypeAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Type()
            db_param.name_type = addRow["name_type"] if "name_type" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table Type")

        self.write_json(out.to_dict())

@web.route("/api/param/bookpublishing/add")
class BookPublishingAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.MaisonEdition()
            db_param.name_book_publishing = addRow["name_book_publishing"] if "name_book_publishing" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table book_publishing")

        self.write_json(out.to_dict())

@web.route("/api/param/owner/add")
class OwnerAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Proprietaire()
            db_param.name_owner = addRow["name_owner"] if "name_owner" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table owner")

        self.write_json(out.to_dict())

@web.route("/api/param/location/add")
class LocationAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.Emplacement()
            db_param.name_location = addRow["name_location"] if "name_location" in addRow else ""

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table location")

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
        elif tableParam == "saga":
            tableParamObj = saga_db.Saga
        elif tableParam == "version":
            tableParamObj = saga_db.Version           
        elif tableParam == "auteur":
            tableParamObj = saga_db.Auteur  
        elif tableParam == "type":
            tableParamObj = saga_db.Type  
        elif tableParam == "bookpublishing":
            tableParamObj = saga_db.MaisonEdition
        elif tableParam == "owner":
            tableParamObj = saga_db.Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Emplacement

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
        elif tableParam == "saga":
            tableParamObj = saga_db.Saga
        elif tableParam == "version":
            tableParamObj = saga_db.Version  
        elif tableParam == "auteur":
            tableParamObj = saga_db.Auteur  
        elif tableParam == "type":
            tableParamObj = saga_db.Type  
        elif tableParam == "bookpublishing":
            tableParamObj = saga_db.MaisonEdition
        elif tableParam == "owner":
            tableParamObj = saga_db.Proprietaire
        elif tableParam == "location":
            tableParamObj = saga_db.Emplacement

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

