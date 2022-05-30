# -*- coding: utf-8 -*-


import os


def get_config(key_name, default_value=None):
    if not key_name in os.environ:
        if default_value is None:
            print(u"* Configuration : {} -> NOT FOUND /!\\".format(key_name, default_value))
        else:
            print(u"* Configuration : {} = {} (default)".format(key_name, default_value))
    else:
        print(u"* Configuration : {} = {}".format(key_name, os.environ[key_name]))
    return os.environ.get(key_name, default_value)

#for key in sorted(os.environ.keys()):
#    if key.startswith(u"SY_HTTPD_"):
#        print u"* Configuration : {} = {}".format(key, os.environ[key])


print(u"Looking for configuration options...")

# Connexion en local ou en base SQL Server => en utilisant le login windows, (ne fonctionne pas avec le user et password je ne sais pas pourquoi)
DSN_PYODBC = 'Driver={SQL Server};Server=localhost\SQLEXPRESS;Database=db_saga;'
#DRIVER_PYODBC = 
DB_NAME = 'db_saga'


""" 
# A décommenter pour passer sur le server, les variables d'environnements sont configurées sur Epaas
DSN_PYODBC = get_config(u"SAGA_HTTPD_DSN_PYODBC", u"Driver={SQL Server};Server=fr0-vsiaas-8545,10018;Database=DBWV2I92")
DRIVER_PYODBC = get_config(u"SAGA_HTTPD_DRIVER_PYODBC", u"")
DB_NAME = get_config(u"SAGA_HTTPD_DB_NAME", u"DBWV2I92")
"""

HTTP_PORT = get_config(u"SAGA_HTTPD_PORT", 8080)
FRONTEND_URL = get_config(u"SAGA_HTTPD_FRONTEND_URL", u"http://localhost")
ADMIN_CONTACTS = get_config(u"SAGA_HTTPD_ADMIN_CONTACTS", u"jeremy.baucherel@free.fr").split(u",")

print(HTTP_PORT)