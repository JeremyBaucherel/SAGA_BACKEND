# -*- coding: utf-8 -*-

from typing import Any, Generic, List, Optional, TypeVar
from mypy_extensions import TypedDict
import datetime
import hashlib
import json
import os.path
import random
import time
import traceback
import urllib
import urllib.parse
import uuid
import sqlalchemy
import tornado.web
import tornado.template
import config
import asgard_db
#from onelogin.saml2.auth import OneLogin_Saml2_Auth
#from onelogin.saml2.utils import OneLogin_Saml2_Utils

T = TypeVar('T')

class JsonUser (TypedDict):
    connecte: bool
    id: int
    logon: str
    url: str
    nom: str
    prenom: str
    autorisations: List[str]
    rgpd_date: Optional[datetime.datetime]
    
class User (TypedDict):
    connecte: bool
    id: int
    logon: str
    url: str
    nom: str
    prenom: str
    autorisations: List[str]
    rgpd_date: Optional[datetime.datetime]
    _db: Optional[asgard_db.Utilisateur]

class RandomFailError(Exception):
    pass


class RequestHandler(tornado.web.RequestHandler):
    """Default request handler used throughout Asgard API."""

    def init_saml_auth(self, req):
        """
        Initializes the authentication.
        return: the OneLogin_Saml2_Auth object.
        """
        saml_folder = os.path.join(os.path.dirname(__file__), u"..", u"..", u"..", u"saml", u"local")
        auth = OneLogin_Saml2_Auth(req, custom_base_path=saml_folder)
        return auth

    def prepare_saml_request(self, request):
        """
        Translates the HTML request to an flask readable one.
        return: the flask request.
        """    
        # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields

        json_body = {}
        if request.body:
            json_body = urllib.parse.parse_qs(request.body.decode("utf-8"))
            if 'SAMLResponse' in json_body:
                json_body['SAMLResponse'] = json_body['SAMLResponse'][0]

        return {
            'https': 'off',
            'http_host': 'localhost',
            'server_port': 8080,
            'script_name': '/api/sso',
            'get_data': request.query,
            # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
            # 'lowercase_urlencoding': True,
            'post_data': json_body
        }

    def decode_request_body_as_json(self):
        """Convert the request body to JSON."""

        json_obj = tornado.escape.json_decode(self.request.body)
        if not json_obj:
            json_obj = {}
        return json_obj

    def disable_caching(self):
        """Set no-caching HTTP directory in the response."""

        self.set_header(u"Cache-Control", u"no-cache, no-store, must-revalidate")
        self.set_header(u"Pragma", u"no-cache")
        self.set_header(u"Expires", u"0")

    def encode_uri(self, uri_component):
        """Encode `uri_component` to UTF-8 then quote."""

        if uri_component:
            return urllib.quote(uri_component.encode("utf-8"), "")
        else:
            return u""

    def write_error(self, _, **__):
        print(self)

    def get_user_as_json(self) -> Optional[JsonUser]:
        """Return the current user as a dictionnary."""
        
        if self.user:
            user: JsonUser = {
                u"connecte": self.user[u"connecte"],
                u"id": self.user[u"id"],
                u"logon": self.user[u"logon"],
                u"url": self.user[u"url"],
                u"nom": self.user[u"nom"],
                u"prenom": self.user[u"prenom"],
                u"autorisations": self.user[u"autorisations"],
                u"rgpd_date": self.user[u"rgpd_date"],
            }
            return user
        return {}

    def fetch_user(self, logon: str, session_id: str) -> User:
        """Fetch a DB user object from the DB based on (logon, session_id)
        :returns: A dict object corresponding to the user requested
        """
        #req = self.prepare_saml_request(self.request)
        #auth = self.init_saml_auth(req)
        #idp_url = auth.login()

        user = self.get_default_user()

        if self.db_session and session_id and logon:
            logon = logon.upper()
            db_user = self.db_session.query(asgard_db.Utilisateur).filter(asgard_db.Utilisateur.logon == logon).first()
            if db_user and db_user.session_id == session_id:
                user = {
                    u"connecte": True,
                    u"id": db_user.id,
                    u"logon": db_user.logon,
                    u"url": u"/utilisateurs/{}".format(db_user.logon),
                    u"nom": db_user.nom,
                    u"prenom": db_user.prenom,
                    u"autorisations": self._get_user_authorisations(db_user.id),
                    u"rgpd_date": db_user.rgpd_date,
                    u"_db": db_user,
                    #u"sso_idp": idp_url
                    u"sso_idp": None,
                }
                db_user.action_date = datetime.datetime.now()
            self.db_session.commit()

        return user

    def has_authorisation(self, authorisation):
        """Checks wether current user has `authorisation`.
        :param authorisation: authorisation name
        :return: True if user has `authorisation`
        """

        return authorisation in self.user[u"autorisations"]

    def is_logged_in(self):
        """Checks whether user is logged in (or is anonymouse)."""

        return self.user[u"connecte"]

    def _get_user_authorisations(self, user_id: int) -> List[Any]:
        """Fetch the authorisations of a given user.
        :param user_id: DB user ID
        :returns: An array of authorisation names the user has.
        """
        autorisations = []

        if self.db_session:
            qry = self.db_session.query(asgard_db.Autorisation) \
                .join(asgard_db.RoleAutorisation) \
                .join(asgard_db.Role) \
                .join(asgard_db.UtilisateurRole) \
                .filter(asgard_db.UtilisateurRole.id_users == user_id)

            for authorisation in qry.all():
                autorisations.append(authorisation.nom)

        return autorisations

    def _get_user_roles(self, user_id: int) -> List[Any]:
        """Fetch the roles of a given user.
        :param user_id: DB user ID
        :returns: An array of role names the user has.
        """
        roles = []

        if self.db_session:
            qry = self.db_session.query(asgard_db.Role) \
                .join(asgard_db.UtilisateurRole) \
                .filter(asgard_db.UtilisateurRole.id_users == user_id)

            for role in qry.all():
                roles.append(role.nom)

        return roles

    def _get_user_gammes(self, user_id: int) -> List[Any]:
        """Fetch the gammes of a given user.
        :param user_id: DB user ID
        :returns: An array of role names the user has.
        """
        gammes = []

        if self.db_session:
            qry = self.db_session.query(asgard_db.RoutingGTI) \
                .join(asgard_db.UsersRoutingGTI) \
                .filter(asgard_db.UsersRoutingGTI.id_users == user_id)

            for gamme in qry.all():
                gammes.append(str(gamme.CptGrpGamme)+"|"+str(gamme.Gamme))

        return gammes

    def on_finish(self):
        """Close the DB connection."""
        if self.db_session:
            self.db_session.close()
            self.db_session = None

    def options(self, *_):
        # no body
        self.set_status(204)
        self.finish()

    def prepare(self):
        """Prepare the HTTP response by opening a DB connection and fetching the current
        user.
        """

        self.db_session = sqlalchemy.orm.sessionmaker(bind=self.settings[u"db_engine"])()
        session_logon = self.get_cookie(u"session_logon", "") #.decode("utf-8")
        session_id = self.get_cookie(u"session_id", "") #.decode("utf-8")

        self.user = self.fetch_user(session_logon, session_id)
      

    def set_default_headers(self):
        """Set default HTTP headers to allow CORS requests."""

        self.set_header(u"Access-Control-Allow-Origin", config.FRONTEND_URL)
        self.set_header(u"Access-Control-Allow-Headers", u"x-requested-with")
        self.set_header(u"Access-Control-Allow-Methods", u"POST, PUT, GET, OPTIONS, DELETE")
        self.set_header(u"Access-Control-Allow-Credentials", u"true")

    def sign_in(self, logon: str, pwd: str) -> Optional[asgard_db.Utilisateur]:
        """Sign a user in.
        :returns: A DB user object if sign in was successfull, None otherwise.
        """

        if logon and pwd and self.db_session:
            db_user = self.db_session.query(asgard_db.Utilisateur).filter(asgard_db.Utilisateur.logon == logon.upper()).first()

            if db_user:
                hash_method = db_user.mdp_methode
                if hash_method:
                    _, hash_salt = hash_method.split(u":")
                else:
                    _, hash_salt = u"", u""

                hasher = hashlib.sha512()
                hasher.update(u"{}:{}:ASGARD".format(hash_salt, pwd).encode("utf-8"))
                hashed_password = hasher.hexdigest()

                if hashed_password == db_user.mdp:
                    db_user.session_id = str(uuid.uuid4())
                    self.db_session.commit()
                    # => Suppression car cookie généré par le frontent (sign-in-page.tsx via la librairie cookie.ts)
                    #cookie_expiration_date = datetime.datetime.now() + datetime.timedelta(days=7)
                    #self.set_cookie('session_logon', db_user.logon, expires=cookie_expiration_date)
                    #self.set_cookie('session_id', db_user.session_id, expires=cookie_expiration_date)
                    return db_user

        return None

    def sign_out(self):
        """Sign a user out.
        :returns: True if user was signed out
        """

        session_logon = self.get_cookie(u"session_logon", None) #.decode(u"utf-8")
        session_id = self.get_cookie(u"session_id", None) #.decode(u"utf-8")

        self.user = self.fetch_user(session_logon, session_id)
        if self.user[u"logon"] and self.db_session:
            if self.user[u"_db"]:
                self.user[u"_db"].session_id = u""
                self.db_session.commit()
            self.user = self.get_default_user()
            return True
        else:
            self.user = self.get_default_user()
            return False

    def get_default_user(self) -> User:
        """Build an anonymouse user.
        :returns: A dict object.
        """

        return {
            u"id": 0,
            u"connecte": False,
            u"logon": u"",
            u"nom": u"VADOR",
            u"prenom": u"Dark",
            u"autorisations": [],
            u"rgpd_date": None,
            u"url": u"",
            u"_db": None,
            u"sso_idp": None,
        }

    def sleep_random(self, duration_min, duration_max):
        """Sleep during a random time range.
        Only usefull during development.
        """

        time.sleep(random.uniform(duration_min, duration_max))

    def fail_randomly(self):
        """Fail randomly (not eveytime).
        Only usefull during development
        """

        if random.randint(1, 10) == 5:
            raise RandomFailError()


class JsonResponse(Generic[T]):
    """A JSON HTTP response to API REST requests."""

    body: Optional[T]

    def __init__(self):
        self.errors = {}
        self.body = None

    def add_error(self, section, error):
        """Add an error to the response.
        :param section: Section name to add error to.
        :param error: Error message to add.
        """

        if not section in self.errors:
            self.errors[section] = []
        self.errors[section].append(error)

    def ensure(self, condition, error_section, error_message):
        """Check that `condition` is True, otherwise add `error_message` to `error_section`."""

        if not condition:
            self.add_error(error_section, error_message)

    def ensure_user_is_logged_in(self, user):
        """Check that a user is logged in, otherwise add an error."""

        if not user[u"connecte"]:
            self.add_error(u"user", u"Vous n'êtes pas connecté à votre compte utilisateur")

    def ensure_user_has_authorization(self, user, authorization):
        """Check that a user has a given `authorization`, otherwise add an error.
        :param user: Dict user object
        :param authorization: Name of the authorization
        """

        if not authorization in user[u"autorisations"]:
            self.add_error(u"user", u"Il vous manque une autorisation ({})".format(authorization))

    def ensure_user_has_any_authorization(self, user, authorizations):
        """Check that a user has at least one authorization in `authorizations`, otherwise add an error.
        :param user: Dict user object
        :param authorization: List of authorizations
        """

        has_any_authorization = False
        for authorization in authorizations:
            if authorization in user[u"autorisations"]:
                has_any_authorization = True

        if not has_any_authorization:
            self.add_error(u"user", u"Il vous manque des autorisations parmi {}".format(u",".join(authorizations)))

    def ok(self):
        """Return True if response has no error."""

        return len(self.errors) == 0

    def nok(self):
        """Return True if response has at least 1 error."""

        return len(self.errors) > 0

    def set_body(self, body):
        """Set response body.
        :param body: Dict object to be used as response (will be converted to JSON)
        """

        self.body = body

    def to_dict(self):
        """Build a Dict object to represent the HTTP response body."""

        status = u"NOK"
        if self.ok():
            status = u"OK"

        errors = []
        for errs in self.errors.values():
            for err in errs:
                errors.append(err)

        resp = {
            u"status": status,
            u"errors": self.errors,
            u"errorsSummary": u"\r\n".join(errors),
            u"body": self.body,
        }
        return resp
        

class JsonHandler(RequestHandler):
    """An HTTP response with JSON body."""

    class ErrorResponse(TypedDict):
        method: str
        path: str
        uri: str
        query: str
        handler: str

    def parse_json_body(self) -> Any:
        """Parse the request body (encoded as UTF-8) as JSON."""

        if self.request.body:
            obj = tornado.escape.json_decode(self.request.body.decode('utf-8'))
            return obj
        else:
            return {}

    def write_error(self, status_code: int, **_: Any) -> None:
        err: JsonHandler.ErrorResponse = {
            u"method": self.request.method,
            u"path": self.request.path,
            u"uri": self.request.uri,
            u"query": self.request.query,
            u"handler": self.__class__.__name__
        }

        out = JsonResponse[JsonHandler.ErrorResponse]()
        out.add_error(u"Http", u"Une erreur inattendue s'est produite (code {})".format(status_code))
        out.set_body(err)
        self.set_header(u"Access-Control-Allow-Origin", config.FRONTEND_URL)
        self.write_json(out.to_dict())

    def write_json(self, out):
        #self.sleep_random(0, 0.5)
        #self.fail_randomly()
        self.disable_caching()

        allowed_origin = config.FRONTEND_URL
        # Accept both HTTP and HTTPS requests coming from the FRONTEND_URL
        # FIXME Why was this useful ?
        #if u"origin" in self.request.headers:
        #    if self.request.headers[u"origin"].endswith(u"://{}".format(frontend_hostname)):
        #        allowed_origin = self.request.headers[u"origin"]

        self.set_header(u"Access-Control-Allow-Origin", allowed_origin)
        self.set_header(u"Access-Control-Allow-Methods", u"GET, POST")
        self.set_header(u"Access-Control-Allow-Credentials", u"true")
        self.set_header(u"Access-Control-Allow-Headers", u"Content-Type, *")

        self.set_header(u"Content-Type", u"application/json; charset=\"utf-8\"")
        self.write(json.dumps(out, indent=4, default=self.json_serial))
        self.finish()

    @classmethod
    def json_serial(cls, obj: Any) -> Any:
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable {}".format(type(obj)))
