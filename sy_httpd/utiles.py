# -*- coding: utf-8 -*-
'''
    utiles.py
    Ici on retrouve tous les codes utiles génériques pour le developpement d'applications
'''
import base64
import pandas as pd

def JsonToCSV(input, output, sep=";", orient='columns', usecols=None):
    '''
        Fonction qui va permettre de convertir un fichier json en un fichier csv
        :param input: Chemin vers le fichier json à convertir, ex: chemin/fichier.json
        :param output: Chemin de sortie pour le fichier résultat csv, ex: chemin/fichier.csv
        :param sep: Séparateur pour le fichier csv
        :param orient: Orientation pour la lecture du fichier Json, par défaut 'columns'
        :param usecols: Liste des colonnes à garder si différentes du fichier d'entrée
    '''
    # Récupération du contenu du fichier Json
    df = pd.read_json(input, orient=orient)

    # Filtre
    if usecols!= None: df = df[usecols]

    # export result in csv file
    df.to_csv(output, index = False, sep=str(sep))

def CSVToJson(input, output, sep=";", orient='records', indent=4, usecols=None):
    '''
        Fonction qui va permettre de convertir un fichier csv en un fichier Json
        :param input: Chemin vers le fichier csv à convertir, ex: chemin/fichier.csv
        :param output: Chemin de sortie pour le fichier résultat json, ex: chemin/fichier.json
        :param sep: Séparateur pour le fichier csv
        :param orient: Orientation d'écriture du fichier Json, par défaut 'records'
        :param indent: Indentation pour l'écriture du fichier json, par défaut 4
        :param usecols: Liste des colonnes à garder dans fichier csv d'entrée
    '''
    # Lecture du csv pour récupérer la relation MP / List of MSN
    df = pd.read_csv(input, sep=sep, usecols=usecols)

    # Enregistrement du fichier Json Résultat avec la nouvelle colonne Effectivity en plus
    jsonText = df.to_json(orient=orient, indent=indent) #'columns'
    jsonFile = open(output, 'w+')
    jsonFile.write(jsonText)
    jsonFile.close()

def dataFrameToJson(df, output, orient='records', indent=4):
    '''
        Fonction qui va convertir un dataFrame en fichier Json
        :param df: dataframe input
        :param output: chemin/fichier.json
        :param orient: Orientation d'écriture du fichier Json, par défaut 'records'
        :param indent: Indentation pour l'écriture du fichier json, par défaut 4
    '''
    jsonText = df.to_json(orient=orient, indent=indent) #'columns'
    jsonFile = open(output, 'w+')
    jsonFile.write(jsonText)
    jsonFile.close()

def addColumnDataframe(columnTitle, columnContent, df):
    """
        Fonction qui ajoute une colonne à un Dataframe avec un contenu constant (même info dans toutes les lignes)
    
        :param columnTitle: Nom de la colonne à ajouter
        :param columnContent: Contenu à ajouter, le même pour toutes les lignes
        :param df: Dataframe
    """
    df.loc[-1] = [columnTitle, columnContent]  # add column
    df.index = df.index + 1  # shifting index
    df = df.sort_index()  # sorting by index
    return df

def suppDoublonList(myList):
    """
        Fonction qui permet de supprimer les doublons du tableau passé en paramètre
        :param myList: Tableau auquel il faut retirer les valeurs en doublon
        :returns: Tableau sans les doublons
    """
    resultantList = []
    for element in myList:
        if element not in resultantList:
            resultantList.append(element)
    return resultantList

def isNaN(num):
    """
        Fonction qui test si le Terme est Nan
        :param num: Terme à tester
        :returns: Retourne True ou False
    """    
    return num!= num

def fillNbDigit(text, nb):
    """
        Complète un string avec des 0 au début du text
    
        :param text:
        :param nb:
        :returns: Retourne le texte demandé avec le nombre de 0 voulu
    """
    return str(text).zfill(nb)

def createList(r1, r2): 
    """
        Création d'une liste à partir d'une plage, r1 debut de plage, r2 fin de la plage
        :param r1: Début de la liste
        :param r1: Fin de la liste
        :returns: List allant de r1 à r2
    """
    return list(range(r1, r2+1))

def base64_encode(message):
    """
        Encodage en base 64
        :param message: Message à encoder en base64
        :returns: Message encodé en base 64
    """
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii')

def base64_decode(message):
    """
        Decodage en base 64
        :param message: Message en base64 à décoder
        
        :returns: Message décodé à partir d'un encodage en base 64
    """
    base64_bytes = message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('ascii')

def index_in_list(a_list, index):
    """
        Fonction qui vérifie si l'index demandé existe dans le tableau
    
        :param a_list: Liste dans laquelle on souhaite vérifier si l'index existe
        :param index: Index à vérifier
        :returns: True ou False
    """
    return True if index < len(a_list) else False

def indexTab(tab, index, defaut=""):
    """
        Retourne la valeur de l'index demandé dans un tableau si celui-ci existe
        :param tab: Tableau à parcourir
        :param index: Index recherché
        :param defaut: Valeur par défaut à retourner si l'index n'est pas trouvé
        :returns:
    """
    return tab[index] if index_in_list(tab, index) else defaut
