# -*- coding: utf-8 -*-
import urllib.parse
import configparser
import codecs
import utiles as u
from typing import Optional, Union
import os

# Fichier de configuration
FICHIER_INI = 'C://Users//Public//Documents//GitHub//config.ini'

class SapConfig (object):

    def __init__ (self, config):
        self._config = config
    
    def __getitem__ (self, sap_id):
        items = {}
        con_str = self._config.get(u"SAP", sap_id)
        con_qs = urllib.parse.parse_qs(con_str)
        for key, item in con_qs.items():
            if key.lower() == "password": item[0] = u.base64_decode(item[0])
            items[key.lower()] = item[0]
        items[u"sap"] = sap_id
        return items

_config = configparser.SafeConfigParser()
_config.readfp(codecs.open(FICHIER_INI, "r", "latin-1"))
SAP = SapConfig(_config)

#print(SAP["pgi"])

def createVar(nameVar, initValue=None):
    myGlobals = globals()
    if nameVar not in myGlobals:
        myGlobals[nameVar] = initValue
    else:
        raise KeyError("Key exist in {}".format(repr(myGlobals)))

config = configparser.ConfigParser()

# Read the .ini file
config.read(FICHIER_INI)

# List .ini Section and create global variable
for s in config.sections():
    for key in config[s]:
        # Si une variable d'environnement existe elle est prioritaire sur la valeur de la même variable du fichier config.ini
        value = config[s][key] if not key in os.environ else os.environ.get(key)
        createVar(key, value)


print(u"Looking for configuration options...")

HTTP_PORT = 8080
FRONTEND_URL = "http://localhost"
ADMIN_CONTACTS = ["SP0016C7"]