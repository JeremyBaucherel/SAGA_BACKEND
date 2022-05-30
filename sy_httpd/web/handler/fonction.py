# -*- coding: utf-8 -*-
import tornado.escape
import web.handler

# Fonction qui va retourner le bon objet json lorsque l'on souhaite utiliser le complément "FormList"
def result_requete_FormList(obj_self, requete, variable={}):
	db_qn = obj_self.db_session.execute(requete, variable)
	out = web.handler.JsonResponse()
	tab_result = []
	obj = {}
	for row in db_qn:
		obj["id"] = row['id']
		obj["nom"] = row['nom']
		tab_result.append(obj)
		obj = {}
	out.body = tab_result
	return out.to_dict()


# Fonction qui va retourner un objet JSON de la forme clef valeur
def result_requete_keyVal(obj_self, requete, variable={}):
	db_qn = obj_self.db_session.execute(requete, variable)
	out = web.handler.JsonResponse()
	out.body = {}
	for row in db_qn:
		for key in row.keys():
			out.body[key] = row[key] if row[key] else ""
	return out.to_dict()
