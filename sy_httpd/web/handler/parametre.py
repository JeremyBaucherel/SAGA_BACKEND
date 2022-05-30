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

"""
@web.route("/api/param/others")
class ParamOtherHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        process = params.get("process", "")
        authorization = params.get("authorization", "")

        qry = self.db_session.query(saga_db.ParamOther) \
                .filter(saga_db.ParamOther.processName == process) \
                .order_by(saga_db.ParamOther.categorie, saga_db.ParamOther.nom)

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            ParamOthers=[]
            for param in qry.all():  

                ParamOthers.append({
                    "id": param.id,
                    "processName": param.processName,
                    "categorie": param.categorie,
                    "nom": param.nom,
                    "valeur": param.valeur,
                    "description": param.description,
                    "actif": param.actif,
                })

            out.set_body(ParamOthers)

        self.write_json(out.to_dict())

@web.route("/api/param/gti")
class ParamGtiHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        process = params.get("process", "")

        if process == "METALLISATION":
            authorization = 'METAL:DISPLAY'
        elif process == "FIBREOPTIQUE":
            authorization = 'OPTIQUE:DISPLAY'

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            qry = self.db_session.query(saga_db.ParamGTI) \
                .join(saga_db.RoutingGTI) \
                .join(saga_db.UsersRoutingGTI) \
                .join(saga_db.ProcessRoutingGTI) \
                .filter(saga_db.ProcessRoutingGTI.processName == process) \
                .filter(saga_db.ProcessRoutingGTI.id_statut == 3) \
                .filter(saga_db.UsersRoutingGTI.id_users == user_id) \
                .order_by(saga_db.ParamGTI.Gamme)
    
            ParamGti=[]
            for gti in qry.all():  
                ParamGti.append({
                    "id": gti.id,
                    "GTI": gti.GTI,
                    "DocType": gti.DocType,
                    "Part": gti.Part,
                    "Gamme": gti.Gamme,
                    "cptGrGam": gti.cptGrGam,
                    "Operation": gti.Operation,
                    "creationStatut": gti.creationStatut,
                    "nbDigitMsnSap": gti.nbDigitMsnSap,
                    "groupeGestionnaire": gti.groupeGestionnaire,
                    "DesignationsCSV": gti.DesignationsCSV,
                    "Section": gti.Section,
                    "processName": gti.processName,
                    "Libelle": gti.Libelle,
                    "NumDocMsn": gti.NumDocMsn,
                    "pvnameCSV": gti.pvnameCSV,
                    "pvnamePDF": gti.pvnamePDF,
                    "folderpv": gti.folderpv,
                    "Zone": gti.Zone,
                    "Langue": gti.Langue,
                    "LongTitle": gti.LongTitle,
                    "ShortTitle": gti.ShortTitle,
                })

            out.set_body(ParamGti)

        self.write_json(out.to_dict())

@web.route("/api/param/ParamOther/add")
class ParamOtherAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        process = params.get("process", "")
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            db_param = saga_db.ParamOther()
            db_param.processName = process
            db_param.categorie = addRow["categorie"] if "categorie" in addRow else ""
            db_param.nom = addRow["nom"] if "nom" in addRow else ""
            db_param.valeur = addRow["valeur"] if "valeur" in addRow else ""
            db_param.description = addRow["description"] if "description" in addRow else ""
            db_param.actif = addRow["actif"] if "actif" in addRow else 0

            self.db_session.add(db_param)
            self.db_session.commit()

            out.set_body("Nouvelle ligne ajoutée dans la table ParamOther")

        self.write_json(out.to_dict())
"""

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

"""
@web.route("/api/param/ParamGTI/add")
class ParamGTIAddHandler(web.handler.JsonHandler):

    def post(self):

        user_id = self.user["id"]

        params = self.parse_json_body()
        process = params.get("process", "")
        authorization = params.get("authorization", "")
        addRow = params.get("addRow", "")

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            # Recherche de l'id_routingGTI correspond dans la table RoutingGTI
            rech_id_routingGTI = self._get_id_routingGTI(self.db_session, addRow["Gamme"], addRow["cptGrGam"])
            if not rech_id_routingGTI:
                out.add_error(u"ParamGTI", u"Impossible d'ajouter une nouvelle ligne dans la table. Vous n'avez pas entré un couple Gamme / Compteur Groupe de Gamme qui corresponde au Process: " + process)
            else:
                id_routingGTI = rech_id_routingGTI.id

                db_param = saga_db.ParamGTI()
                db_param.id_routingGTI = id_routingGTI
                db_param.GTI = addRow["GTI"] if "GTI" in addRow else ""
                db_param.DocType = addRow["DocType"] if "DocType" in addRow else ""
                db_param.Part = addRow["Part"] if "Part" in addRow else ""
                db_param.Gamme = addRow["Gamme"] if "Gamme" in addRow else ""
                db_param.cptGrGam = addRow["cptGrGam"] if "cptGrGam" in addRow else ""
                db_param.Operation = addRow["Operation"] if "Operation" in addRow else ""
                db_param.creationStatut = addRow["creationStatut"] if "creationStatut" in addRow else 0
                db_param.nbDigitMsnSap = addRow["nbDigitMsnSap"] if "nbDigitMsnSap" in addRow else ""
                db_param.groupeGestionnaire = addRow["groupeGestionnaire"] if "groupeGestionnaire" in addRow else ""
                db_param.DesignationsCSV = addRow["DesignationsCSV"] if "DesignationsCSV" in addRow else ""
                db_param.Section = addRow["Section"] if "Section" in addRow else ""
                db_param.processName = process
                db_param.Libelle = addRow["Libelle"] if "Libelle" in addRow else ""
                db_param.NumDocMsn = addRow["NumDocMsn"] if "NumDocMsn" in addRow else ""
                db_param.pvnameCSV = addRow["pvnameCSV"] if "pvnameCSV" in addRow else ""
                db_param.pvnamePDF = addRow["pvnamePDF"] if "pvnamePDF" in addRow else ""
                db_param.folderpv = addRow["folderpv"] if "folderpv" in addRow else ""
                db_param.Zone = addRow["Zone"] if "Zone" in addRow else ""   
                db_param.Langue = addRow["Langue"] if "Langue" in addRow else ""
                db_param.LongTitle = addRow["LongTitle"] if "LongTitle" in addRow else ""
                db_param.ShortTitle = addRow["ShortTitle"] if "ShortTitle" in addRow else ""

                self.db_session.add(db_param)
                self.db_session.commit()

                out.set_body("Nouvelle ligne ajoutée dans la table ParamGTI")

        self.write_json(out.to_dict())


    def _get_id_routingGTI(self, db_session, gamme, cptGrGam) -> Optional[saga_db.RoutingGTI]:
        if db_session:
            query = db_session.query(saga_db.RoutingGTI) \
                .filter(saga_db.RoutingGTI.Gamme == gamme) \
                .filter(saga_db.RoutingGTI.CptGrpGamme == cptGrGam)
            return query.first()
        return []
"""
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

"""
@web.route("/api/param/:tableParam/edit")
class ParamEditHandler(web.handler.JsonHandler):

    def post(self, tableParam:str) -> None:

        user_id = self.user["id"]

        params = self.parse_json_body()
        authorization = params.get("authorization", "")
        saveRows = params.get("saveRows", "")

        if tableParam == "ParamPFE":
            tableParamObj = saga_db.ParamPFE
        elif tableParam == "ParamGTI":
            tableParamObj = saga_db.ParamGTI
        elif tableParam == "ParamMetalFullConf_A320":
            tableParamObj = saga_db.ParamMetalFullConf_A320
        elif tableParam == "version":
            tableParamObj = saga_db.Version
        elif tableParam == "ParamTrag_TypePin":
            tableParamObj = saga_db.ParamTrag_TypePin
        elif tableParam == "ParamTrag_TypeCable":
            tableParamObj = saga_db.ParamTrag_TypeCable
        elif tableParam == "ParamOther":
            tableParamObj = saga_db.ParamOther
        elif tableParam == "Role":
            tableParamObj = saga_db.Role       
        elif tableParam == "Autorisation":
            tableParamObj = saga_db.Autorisation       
        elif tableParam == "RoutingGTI":
            tableParamObj = saga_db.RoutingGTI

        out = web.handler.JsonResponse()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, authorization)

        if out.ok() and user_id:

            for v in saveRows:
                rowId = v["id"]
                columnName = v['columnName']
                value = v['value']
                colId = "id"

                if tableParam == "RoutingGTI": 
                    if columnName == "statut" or columnName == "processName":
                        tableParamObj = saga_db.ProcessRoutingGTI
                        colId = "id_routingGTI"
                    if columnName == "statut": 
                        columnName = "id_statut"

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

        if tableParam == "ParamPFE":
            tableParamObj = saga_db.ParamPFE
        elif tableParam == "ParamGTI":
            tableParamObj = saga_db.ParamGTI
        elif tableParam == "ParamMetalFullConf_A320":
            tableParamObj = saga_db.ParamMetalFullConf_A320
        elif tableParam == "version":
            tableParamObj = saga_db.Version
        elif tableParam == "ParamTrag_TypePin":
            tableParamObj = saga_db.ParamTrag_TypePin
        elif tableParam == "ParamTrag_TypeCable":
            tableParamObj = saga_db.ParamTrag_TypeCable
        elif tableParam == "ParamOther":
            tableParamObj = saga_db.ParamOther
        elif tableParam == "Role":
            tableParamObj = saga_db.Role       
        elif tableParam == "Autorisation":
            tableParamObj = saga_db.Autorisation    
        elif tableParam == "RoutingGTI":    # ATTENTION IL Y A DES TABLES LIEES !!!! QUE FAIRE ???
            tableParamObj = saga_db.RoutingGTI

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

            if tableParam == "RoutingGTI":
                self.delProcessRoutingGTI(rowId)
                # Si on a des données dans ces tablea qu'estce que l'on fait ???
                # ProcessPV
                # ParamCOMS
                # ParamGTI
                # ProcessPFE

            out.set_body("Id " + str(rowId) + " supprimé dans la table " + tableParam)

        self.write_json(out.to_dict())
    
    def delProcessRoutingGTI(self, rowId):
        statement = delete(saga_db.ProcessRoutingGTI).where(saga_db.ProcessRoutingGTI.id_routingGTI==rowId)
        self.db_session.execute(statement)
        self.db_session.commit()

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
"""
