from typing import Any, Dict, List, Optional, Tuple
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

@web.route(u"/api/utilisateurs/roles")
class RolesHandler(web.handler.JsonHandler):

    class JsonRole(TypedDict):
        id: int
        name: str
        description: str

    def get(self) -> None:
        """Return a list of the roles the current user has."""

        resp = web.handler.JsonResponse[List[RolesHandler.JsonRole]]()
        resp.set_body(self._get_roles())
        self.write_json(resp.to_dict())

    def _get_roles(self) -> List['RolesHandler.JsonRole']:
        roles: List[RolesHandler.JsonRole] = []
        
        if self.db_session:
            qry = self.db_session.query(saga_db.Role).all()
            
            for db_role in qry:
                role: RolesHandler.JsonRole = {
                    u"id": db_role.id,
                    u"name": db_role.nom,
                    u"description": db_role.description,
                }

                roles.append(role)

        return roles


@web.route(u"/api/utilisateurs/connexion")
class SignInHandler(web.handler.JsonHandler):

    def post(self) -> None:
        """Try to sign-in a user."""
        
        params = self.decode_request_body_as_json()
        logon = params.get("logon", None)
        pwd = params.get("password", None)
        db_user = self.sign_in(logon, pwd)

        out = web.handler.JsonResponse()
        out.ensure(logon, u"logon", u"Veuillez renseigner votre logon")
        out.ensure(pwd, u"password", u"Veuillez renseigner votre mot de passe")
        out.ensure(db_user, u"user", u"Aucun compte n'a été trouvé pour ces informations")

        if out.ok() and db_user:
            self.user = self.fetch_user(logon, db_user.session_id)
            user = self.get_user_as_json()

            out.set_body({
                u"user": user,
                u"auth": {
                    u"logon": db_user.logon,
                    u"sessionId": db_user.session_id
                }
            })

        self.write_json(out.to_dict())


@web.route(u"/api/utilisateurs/deconnexion")
class SignOutHandler(web.handler.JsonHandler):

    class PostResponse (TypedDict):
        user: Optional[web.handler.JsonUser]

    def post(self) -> None:
        """Sign-out the current user."""

        success = self.sign_out()

        out = web.handler.JsonResponse[SignOutHandler.PostResponse]()
        out.ensure(success, "signout", u"La déconnexion a échoué")

        if out.ok():
            out.set_body({
                u"user": self.get_user_as_json(),
            })

        self.write_json(out.to_dict())

@web.route(u"/api/utilisateurs/:user_logon/autorisations")
class AutorisationsHandler(web.handler.JsonHandler):

    class Autorisation(TypedDict):
        nom: str
        description: str

    class Role(TypedDict):
        id: int
        nom: str
        description: str
        autorisations: List['AutorisationsHandler.Autorisation']

    def get(self, logon: str) -> None:
        """Get a list of the authorizations of a user."""

        db_user = self._get_db_user(logon)

        out = web.handler.JsonResponse[List[AutorisationsHandler.Role]]()
        out.ensure(db_user, u"user", u"L'utilisateur {} est introuvable".format(logon))

        if out.ok() and db_user:
            out.set_body(self._get_roles(db_user.id))

        self.write_json(out.to_dict())

    def _get_db_user(self, logon: str) -> Optional[saga_db.Utilisateur]:
        """Get a user from the DB by logon."""
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

    def _get_roles(self, user_id: int) -> List['AutorisationsHandler.Role']:
        """Get the roles of a user by user id"""
        roles: List[AutorisationsHandler.Role] = []

        if self.db_session:
            qry = self.db_session.query(saga_db.Role) \
                .join(saga_db.UtilisateurRole) \
                .filter(saga_db.UtilisateurRole.id_users == user_id)

            for role in qry.all():
                roles.append({
                    u"id": role.id,
                    u"nom": role.nom,
                    u"description": role.description,
                    u"autorisations": self._get_autorisations(role.id),
                })

        return sorted(roles, key=lambda x: x[u"nom"])

    def _get_autorisations(self, id_role: int) -> List['AutorisationsHandler.Autorisation']:
        """Get the authorizations for a role (by ID)."""

        autorisations: List[AutorisationsHandler.Autorisation] = []

        if self.db_session:
            qry = self.db_session.query(saga_db.Autorisation) \
                .join(saga_db.RoleAutorisation) \
                .filter(saga_db.RoleAutorisation.id_role == id_role)

            for aut in qry.all():
                autorisations.append({
                    u"nom": aut.nom,
                    u"description": aut.description,
                })

        return sorted(autorisations, key=lambda x: x[u"nom"])

@web.route(u"/api/utilisateurs/creer")
class CreateHandler(web.handler.JsonHandler):

    class PostResponseJson(TypedDict):
        sessionId: str

    def post(self) -> None:
        """Create a new user"""

        params = self.decode_request_body_as_json()

        request_logon = params.get(u"logon", u"").upper()
        request_first_name = params.get(u"name", u"")
        request_family_name = params.get(u"familyName", u"")
        request_roles = params.get(u"roles", [1003])
        request_send_mail = params.get(u"sendEmail", False)

        db_user = self.get_user_by_logon(request_logon)

        out = web.handler.JsonResponse[CreateHandler.PostResponseJson]()
        out.ensure_user_is_logged_in(self.user)
        out.ensure_user_has_authorization(self.user, u"UTILISATEUR:ADD")
        out.ensure(request_logon, u"logon", u"L'utilisateur doit avoir un logon")
        out.ensure(request_logon and len(request_logon) >= 5, u"logon", u"Le logon doit faire 5 caractères minimum ({} actuellement)".format(len(request_logon)))
        out.ensure(request_logon and len(request_logon) <= 15, u"logon", u"Le logon doit faire 15 caractères maximum ({} actuellement)".format(len(request_logon)))
        out.ensure(not db_user, u"logon", u"L'utilisateur {} existe déjà.".format(request_logon))
        out.ensure(request_first_name, u"name", u"L'utilisateur doit avoir un prénom.")
        out.ensure(request_family_name, u"familyName", u"L'utilisateur doit avoir un nom de famille.")

        for id_role in request_roles:
            out.ensure(self.get_role(id_role), u"roles", u"Le rôle n'existe pas.")

        if out.ok() and self.db_session:
            db_user = saga_db.Utilisateur()
            db_user.logon = request_logon.upper()
            db_user.prenom = request_first_name
            db_user.nom = request_family_name.upper()
            db_user.session_id = str(uuid.uuid4())
            db_user.mdp = u""
            db_user.action_date = datetime.datetime.now()
            self.db_session.add(db_user)
            self.db_session.commit()

            if request_roles:
                for id_role in request_roles:
                    self.add_role_to_user(db_user, id_role)
                self.db_session.commit()

            out.set_body({u"sessionId": db_user.session_id})

            if not request_send_mail in [False, u"False"]:
                self.send_activation_mail(db_user)

        self.write_json(out.to_dict())

    def add_role_to_user(self, db_user: saga_db.Utilisateur, id_role: int) -> None:
        #FIXME Should fail if no db_session
        if self.db_session:
            user_role = saga_db.UtilisateurRole()
            user_role.id_users = db_user.id
            user_role.id_role = id_role
            self.db_session.add(user_role)

    def send_activation_mail(self, db_user) -> None:
        activation_url = u"{}/utilisateurs/{}/initialiser/{}".format(config.FRONTEND_URL, db_user.logon, db_user.session_id)
        mail_body = u"""
            <p class="subtle">Bonjour {name},</p>
            <br />
            <p><a href="{activation_url}"><strong>Activez votre compte utilisateur SAGA</strong></a></p>
            <br />
            <p>Bonne utilisation !</p>
            <br />
            <p class="subtle">Cordialement,</p>
            <p class="subtle">L'équipe SAGA.<p>
            <br />
            <p class="subtle"><small>P.-S. Vous recevez cet e-mail suite à la création de votre compte par {creator_name} {creator_family_name}.</small></p>
        """.format(
            name=db_user.prenom,
            activation_url=activation_url,
            creator_name=self.user[u"prenom"],
            creator_family_name=self.user[u"nom"],
            )

        mail = sendmail.Mail()
        mail.to = [db_user.logon]
        mail.cc = [u"jeremy.j.baucherel.external@airbus.com"]
        mail.subject = u"[SAGA] Activation compte utilisateur"
        mail.body = u"".join([line.strip() for line in mail_body.splitlines()])
        mail.sendHtml()

    def get_user_by_logon(self, logon: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            logon = logon.upper()
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

    def get_role(self, id_role: int) -> Optional[saga_db.Role]:
        if self.db_session:
            return self.db_session.query(saga_db.Role).get(id_role)
        return None

@web.route(u"/api/utilisateurs/:user_logon/modifier")
class UpdateHandler(web.handler.JsonHandler):

    def post(self, logon: str) -> None:
        """Update a user account"""

        params = self.decode_request_body_as_json()

        request_logon = params.get(u"logon", u"").upper()
        request_first_name = params.get(u"name", u"")
        request_family_name = params.get(u"familyName", u"")
        request_roles = params.get(u"roles", [])
        db_user = self.get_user_by_logon(logon)

        response = web.handler.JsonResponse[None]()
        response.ensure_user_is_logged_in(self.user)
        response.ensure_user_has_any_authorization(self.user, [u"UTILISATEUR:EDIT"])
        response.ensure(request_logon == logon, u"logon", u"Logon incohérent")
        response.ensure(request_logon and len(request_logon) >= 5, u"logon", u"Le logon doit faire 5 caractères minimum ({} actuellement)".format(len(request_logon)))
        response.ensure(request_logon and len(request_logon) <= 15, u"logon", u"Le logon doit faire 15 caractères maximum ({} actuellement)".format(len(request_logon)))
        response.ensure(db_user, u"logon", u"L'utilisateur {} n'existe pas.".format(request_logon))
        response.ensure(request_first_name, u"name", u"L'utilisateur doit avoir un prénom.")
        response.ensure(request_family_name, u"familyName", u"L'utilisateur doit avoir un nom de famille.")

        # Vérifie que les rôles existent dans la base
        if request_roles:
            for id_role in request_roles:
                response.ensure(self.get_role(id_role), u"roles", u"Le rôle n'existe pas.")
        
        if response.ok() and db_user and self.db_session:
            db_user.logon = request_logon.upper()
            db_user.prenom = request_first_name
            db_user.nom = request_family_name.upper()
            self.db_session.commit()

            # Remove old roles
            for db_role in self.get_user_roles(db_user.id):
                if not db_role.id_role in request_roles:
                    self.db_session.delete(db_role)
            if request_roles:
                # Add new roles
                for id_role in request_roles:
                    self.add_role_to_user(db_user, id_role)
            self.db_session.commit()


        self.write_json(response.to_dict())

    def add_role_to_user(self, db_user: saga_db.Utilisateur, id_role: int) -> None:
        if self.db_session and not self.does_user_have_role(db_user.id, id_role):
            user_role = saga_db.UtilisateurRole()
            user_role.id_users = db_user.id
            user_role.id_role = id_role
            self.db_session.add(user_role)

    def get_user_by_logon(self, logon: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            logon = logon.upper()
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

    def get_user_roles(self, user_id: int) -> List[saga_db.UtilisateurRole]:
        if self.db_session:
            return self.db_session.query(saga_db.UtilisateurRole) \
                .filter(saga_db.UtilisateurRole.id_users == user_id) \
                .all()
        return []

    def get_role(self, id_role: int) -> Optional[saga_db.Role]:
        if self.db_session:
            return self.db_session.query(saga_db.Role).get(id_role)
        return None

    def does_user_have_role(self, user_id: int, id_role: int) -> bool:
        if self.db_session:
            return self.db_session.query(saga_db.UtilisateurRole) \
                .filter(saga_db.UtilisateurRole.id_users == user_id) \
                .filter(saga_db.UtilisateurRole.id_role == id_role) \
                .first() != None
        return False


@web.route(u"/api/utilisateurs/:user_logon/initialiser")
class InitHandler(web.handler.JsonHandler):

    def post(self, user_logon: str) -> None:
        """Initialize a user account."""

        response = web.handler.JsonResponse[None]()

        if not self.user[u"connecte"]:
            user_logon = user_logon.upper()
            user = self.get_user(user_logon)

            params = self.parse_json_body()
            password = params.get(u"password", u"")
            password_bis = params.get(u"passwordBis", u"")
            session_id = params.get(u"sessionId", u"")

            if not session_id:
                response.add_error(u"user", u"Numéro d'activation de compte utilisateur absent")
            elif user and user.session_id != session_id:
                response.add_error(u"user", u"Numéro d'activitation de compte utilisateur incorrect.")

            if not password:
                response.add_error(u"password", u"Mot de passe non renseigné")
            elif len(password) < 6:
                response.add_error(u"password", u"Le mot de passe doit faire au minimum 6 caractères ({} actuellement).".format(len(password)))

            if not password_bis:
                response.add_error(u"passwordBis", u"Répétition du mot de passe non renseigné")
            elif password and password != password_bis:
                response.add_error(u"passwordBis", u"Les deux mots de passe doivent être identiques.")

            if response.ok() and user and self.db_session:
                hashed_password, method = self.hash_password(password)
                user.mdp = hashed_password
                user.mdp_methode = method

                self.db_session.commit()

                mail_body = u"""
                <p class="subtle">Bonjour {name},</p>
                <br />
                <p>Nous vous souhaitons la bienvenue dans <a href="{host}">SAGA</a> !</p>
                <br />
                <p><strong>SAGA, qu'est-ce c'est ?</strong></p>
                <p>SAGA est l'application officielle pour les Essais (ZZMI5) de Saint-Nazaire. Elle permet de générer les GTI à partir des spécifications données par les GTR (BE). <br />
                Un paramétrage permet une gestion de configuration simplifiée et une mise à jour des effectivitées dans SAP automatique. <br />
                SAGA permet une liaison avec des applications tiers tel ques TEDS, ESN-BMS ou C@pture.</p>
                <br />
                <p><strong>Comment ouvrir SAGA ?</strong></p>
                <p>SAGA est une application Web, il vous suffit donc d'ouvrir l'URL suivante avec Chrome : <a href="{host}">{host}</a></p>
                <br />
                Pour modifier vos droits d'accès, n'hésitez pas à contacter le support (en copie de ce mail). 
                <br />
                <p>Bonne utilisation !</p>
                <br />
                <p class="subtle">Cordialement,</p>
                <p class="subtle">L'équipe SAGA.</p>
                """.format(name=user.prenom, host=config.FRONTEND_URL)

                mail = sendmail.Mail()
                mail.to = [user_logon]
                mail.cc = config.ADMIN_CONTACTS
                mail.subject = u"[SAGA] Bienvenue {} !".format(user.prenom)
                mail.body = u"\n".join([line.strip() for line in mail_body.splitlines()])
                mail.sendHtml()
        else:
            response.add_error(u"user", u"Vous êtes déjà connecté")

        self.write_json(response.to_dict())

    def get_user(self, logon: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

    def hash_password(self, raw_password: str) -> Tuple[str, str]:
        salt = self.get_random_string(40)
        pwd = u"{}:{}:SAGA".format(salt, raw_password)

        pwd_hash = hashlib.sha512()
        pwd_hash.update(pwd.encode("utf-8"))

        return str(pwd_hash.hexdigest()), u"sha512:{}".format(salt)

    def get_random_string(self, length: int) -> str:
        return u"".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))

@web.route(u"/api/moi")
class MeHandler(web.handler.JsonHandler):

    def get(self) -> None:
        """Get informations about the current user."""

        self.disable_caching()
        out = web.handler.JsonResponse[Optional[web.handler.JsonUser]]()
        out.set_body(self.get_user_as_json())
        self.write_json(out.to_dict())

@web.route(u"/api/moi/rgpd")
class MeRgpdHandler(web.handler.JsonHandler):

    def post(self) -> None:
        """Accept Private Individual Information (PII) collection."""

        db_user = self.user[u"_db"]

        out = web.handler.JsonResponse[None]()
        out.ensure_user_is_logged_in(self.user)
        
        if out.ok() and db_user and self.db_session:
            db_user.rgpd_date = datetime.datetime.now()
            self.db_session.commit()

        self.write_json(out.to_dict())

    def get_user(self, logon: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

class ResetPasswordHandlerResponse(TypedDict):
    logon: str
    name: str
    familyName: str
    url: str

@web.route(u"/api/utilisateurs/:user_logon/reinitialiser-mdp")
class ResetPasswordHandler(web.handler.JsonHandler):

    def post(self, logon: str) -> None:
        params = tornado.escape.json_decode(self.request.body)
        
        password_token = params.get(u"passwordToken", u"")
        db_user = self._get_user(logon, password_token)

        out = web.handler.JsonResponse[ResetPasswordHandlerResponse]()
        out.ensure(password_token, u"token", u"Token d'activation manquant")
        out.ensure(db_user, u"form", u"Ce lien d'activation n'est pas valide")

        if out.ok() and self.db_session:
            db_user.mdp = None
            db_user.mdp_methode = None
            db_user.mdp_token = None
            db_user.session_id = str(uuid.uuid4())
            self.db_session.commit()
            body: ResetPasswordHandlerResponse = {
                u"logon": logon,
                u"name": db_user.prenom,
                u"familyName": db_user.nom,
                u"url": u"/utilisateurs/{}/initialiser/{}".format(db_user.logon, db_user.session_id)
            }
            out.set_body(body)

        self.write_json(out.to_dict())

    def _get_user(self, logon, password_token):
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon, saga_db.Utilisateur.mdp_token.like(password_token)) \
                .first()
        return None

@web.route(u"/api/utilisateurs/reinitialiser-mdp")
class RequestPasswordResetHandler(web.handler.JsonHandler):

    def post(self) -> None:
        out = web.handler.JsonResponse[None]()
        params = tornado.escape.json_decode(self.request.body)

        logon = params.get("logon", None)
        db_user = self.get_user(logon)

        if logon and self.db_session:
            if db_user:
                mdp = b""
                if db_user.mdp:
                    mdp = db_user.mdp.encode('utf8')

                token_hash = hashlib.sha512()
                token_hash.update(db_user.logon.encode('utf8') + b":" + mdp + b":SAGA")

                hashed_token = str(token_hash.hexdigest())
                db_user.mdp_token = hashed_token
                self.db_session.commit()

                url = u"{}/utilisateurs/{}/reinitialiser-mdp/{}".format(config.FRONTEND_URL, db_user.logon, hashed_token)

                mail_body = u"""
                <p>Bonjour {name},</p>
                <br />
                <p>A votre demande, vous trouverez ci-dessous le lien pour réinitialiser votre mot de passe.</p>
                <br />
                <p><a href="{url}"><strong>Réinitialisez votre mot de passe SAGA</strong></a></p>
                <br />
                <p>Si vous n'avez pas fait de demande de réinitialisation de votre mot de passe, veuillez ignorer ce message.</p>
                <br />
                <p>Cordialement,</p>
                <p>L'équipe SAGA.</p>
                """.format(name=db_user.prenom, url=url)

                mail = sendmail.Mail()
                mail.to = [db_user.logon]
                mail.cci = config.ADMIN_CONTACTS
                mail.subject = u"[SAGA] Réinitialisation de votre mot de passe"
                mail.body = u"\n".join([line.strip() for line in mail_body.splitlines()])
                mail.sendHtml()
            else:
                out.add_error(u"logon", u"Ce logon n'a pas encore de compte SAGA.")
        else:
            out.add_error(u"logon", u"Veuillez renseigner votre logon")

        self.write_json(out.to_dict())

    def get_user(self, logon: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur) \
                .filter(saga_db.Utilisateur.logon == logon) \
                .first()
        return None

@web.route(u"/api/utilisateurs")
class UsersHandler(web.handler.JsonHandler):

    class UserJson(TypedDict):
        name: str
        familyName: str
        company: str
        logon: str
        url: str
    
    def get(self) -> None:
        """Get a list of all the users."""

        out = web.handler.JsonResponse[List[UsersHandler.UserJson]]()
        db_users = self._get_db_users()
        users = []
        for db_user in db_users:
            user: UsersHandler.UserJson = {
                u"name": db_user.prenom,
                u"familyName": db_user.nom,
                u"logon": db_user.logon,
                u"autorisations": self._get_user_authorisations(db_user.id),
                u"roles": self._get_user_roles(db_user.id),
                u"url": u"/utilisateurs/{}".format(db_user.logon),
            }
            users.append(user)
        out.set_body(users)
        self.write_json(out.to_dict())

    def _get_db_users(self) -> List[saga_db.Utilisateur]:
        if self.db_session:
            return self.db_session.query(saga_db.Utilisateur)
        return []

@web.route(u"/api/utilisateurs/:user_logon")
class UserHandler(web.handler.JsonHandler):
    """Get a user's detailled informations"""

    class UserJson(TypedDict):
        logon: str
        nom: str
        prenom: str
        active: bool

    def get(self, logon: str) -> None:
        db_user = self._get_db_user(logon, self.get_argument(u"activationToken", u""))

        out = web.handler.JsonResponse[UserHandler.UserJson]()
        out.ensure(db_user, u"user", u"L'utilisateur {} est introuvable".format(logon))

        if out.ok() and db_user:
            out.set_body({
                u"logon": db_user.logon,
                u"nom": db_user.nom,
                u"prenom": db_user.prenom,
                u"active": (db_user.mdp != u"" and not db_user.mdp is None),
                u"autorisations": self._get_user_authorisations(db_user.id),
                u"roles": self._get_user_roles(db_user.id),
            })

        self.write_json(out.to_dict())

    def _get_db_user(self, logon: str, activation_token: str) -> Optional[saga_db.Utilisateur]:
        if self.db_session:
            qry = self.db_session.query(saga_db.Utilisateur).filter(saga_db.Utilisateur.logon == logon)
            if activation_token:
                qry = qry.filter(saga_db.Utilisateur.session_id.like(activation_token))
            return qry.first()
        return None
