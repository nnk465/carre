import asyncio
from datetime import datetime
import os
import json
import time

import dropbox

'''

def modify_pseudo(filename, pseudo, amount=0, remove=False):
    with open(filename, 'r') as f:
        data = json.load(f)

    if remove:
        if pseudo in data:
            del data[pseudo]
    else:
        data[pseudo] = amount

    with open(filename, 'w') as f:
        json.dump(data, f)


def add_pseudo(filename, pseudo, amount=0):
    modify_pseudo(filename, pseudo, amount)


def remove_pseudo(filename, pseudo):
    modify_pseudo(filename, pseudo, remove=True)'''


def check_file_exists(filename):
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, filename)
    if not os.path.exists(file_path):
        with open(filename, 'w') as f:
            json.dump({}, f)
            f.close()


def create_json_file(filename):
    with open(filename, 'w') as f:
        json.dump({}, f)
        f.close()


def add_points(filename, iD: int, amount: int):
    with open(filename, 'r') as f:
        data = json.load(f)
        f.close()
    if str(iD) in data.keys():
        data[str(iD)] += amount
        print(1)
    else:
        data[str(iD)] = amount
        print(2)
    with open(filename, 'w') as f:
        json.dump(data, f)
        f.close()
    return data[str(iD)]


def checkpoints(filename, listId, amount):
    with open(filename, 'r') as f:
        data = json.load(f)
        f.close()
    l1 = []
    l2 = data.keys()
    for iD in listId:
        if str(iD) not in l2 or data[str(iD)] - amount < 0:
            l1.append(iD)
    return l1


def remove_points(filename, iD, amount: int):
    iD = str(iD)
    with open(filename, 'r') as f:
        data = json.load(f)
        f.close()
    if iD in data:
        print(2)
        data[iD] -= amount
        print(3)
    else:
        return 0
    with open(filename, 'w') as f:
        print(5)
        json.dump(data, f)
        f.close()


def upload_to_dropbox(file_path, access_token, destination_path):
    dbx = dropbox.Dropbox(access_token)

    with open(file_path, 'rb') as f:
        try:
            dbx.files_upload(f.read(), destination_path)
            print("Fichier téléversé avec succès dans Dropbox.")
        except dropbox.dropbox_client.ApiError as e:
            print("Une erreur s'est produite lors du téléversement :", e)
        f.close()


async def upload(token, file):
    print('upload')
    dbx = dropbox.Dropbox(token)

    destination_path = f'/data{datetime.now().strftime("%d/%m à %H:%M")}.json'  # Nouveau chemin de destination avec le nouveau nom de fichier

    with open(file, 'rb') as f:
        try:
            dbx.files_upload(f.read(), destination_path)
            print("Fichier téléversé avec succès dans Dropbox.")
        except dropbox.dropbox_client.ApiError as e:
            print("Une erreur s'est produite lors du téléversement :", e)
        f.close()
