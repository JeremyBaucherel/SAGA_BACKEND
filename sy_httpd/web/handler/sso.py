from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils
import config
import datetime
import uuid
import urllib.parse
import web.handler
import tornado.escape


def prepare_request(request):
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


@web.route(u"/api/sso-acs")
class Sso(web.handler.JsonHandler):
    
    def post(self):
        req = self.prepare_saml_request(self.request)
        auth = self.init_saml_auth(req)
        auth.process_response(request_id=None)

        user_attr = auth.get_attributes()
        user_logon = user_attr["urn:oid:0.9.2342.19200300.100.1.1"][0]

        qry = self.db_session.execute("SELECT TOP (1) logon FROM membre WHERE logon=:user_logon", {u"user_logon": user_logon})
        db_user = None
        for db_user in qry:
            pass

        cookie_expiration_date = datetime.datetime.now() + datetime.timedelta(days=1)

        if db_user:
            session_id = str(uuid.uuid4())
            
            self.set_cookie('session_logon', user_logon, expires=cookie_expiration_date)
            self.set_cookie('session_id', session_id, expires=cookie_expiration_date)

            self.db_session.execute(u"UPDATE membre SET session_id=:session_id WHERE logon=:user_logon", {u"user_logon": user_logon, u"session_id": session_id})
            self.db_session.commit()
        else:
            qry = self.db_session.execute("SELECT TOP (1) logon, session_id FROM membre WHERE logon='anonyme'")
            db_user = None
            for db_user in qry:
                self.set_cookie('session_logon', db_user[0], expires=cookie_expiration_date)
                self.set_cookie('session_id', db_user[1], expires=cookie_expiration_date)

        self.redirect(config.FRONTEND_URL)
