# -*- coding: utf-8 -*-

ROUTES = []

def route(route_str):
    route_str = route_str.replace(u":user_logon", u"([^/]+)")
    route_str = route_str.replace(u":tableParam", u"([^/]+)")

    #route_str = route_str.replace(u":team_name", u"([^/]+)")
    #route_str = route_str.replace(u":date_ymd", u"([0-9]+)")
    #route_str = route_str.replace(u":folder_id", u"([0-9]+)")
    #route_str = route_str.replace(u":qn_ref", u"([0-9]+)")
    #route_str = route_str.replace(u":table_name", u"(avis|divergence)")
    
    #route_str = route_str.replace(u":cluster_id", u"([^/-.]+)")
    #route_str = route_str.replace(u":cluster_type", u"(defauts|causes|localisations|machines|outils|reparations)")
    #route_str = route_str.replace(u":part_family_name", u"([^/]+)")
    #route_str = route_str.replace(u":part_number", u"([^/]+)")

    def add_route(cls):
        ROUTES.append((route_str, cls))
        return cls

    return add_route
