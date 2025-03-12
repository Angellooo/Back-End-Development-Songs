from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    url = f"mongodb://{mongodb_username}:{mongodb_password}@{mongodb_service}"
else:
    url = f"mongodb://{mongodb_service}"


print(f"connecting to url: {url}")

try:
    client = MongoClient(url)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.drop()
db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

@app.route("/health")
def health():
    return {"status":"ok"}, 200
    # Angello Gonzalez

@app.route("/count")
def count_songs():
    songs_count = len(songs_list)
    return {"count" : songs_count}, 200
    # Angello Gonzalez

@app.route("/song")
def songs():
    songs_docs = list(db.songs.find({}))
    return {"songs":json_util.dumps(songs_docs)}, 200
    # Angello Gonzalez

@app.route("/song/<id>")
def get_song_by_id(id):
    song_single_doc = db.songs.find_one({"id":int(id)})
    if song_single_doc:
        return json_util.dumps(song_single_doc), 200
    else:
        return {"message": "song with id not found"}, 404
    # Angello Gonzalez

@app.route("/song", methods=['POST'])
def create_song():
    json_body = request.get_json()
    if db.songs.find_one({"id":json_body['id']}):
        return {"Message": f"song with id {json_body['id']} already present"}, 302
    else:
        insertion_response = db.songs.insert_one(json_body)
        insertion_oid = str(insertion_response.inserted_id)
        return {"inserted id":{"$oid":insertion_oid}}
    # Angello Gonzalez

@app.route("/song/<int:id>", methods=['PUT'])
def update_song(id):
    json_body = request.get_json()

    if db.songs.find_one({"id":id}):
        result = db.songs.update_one({"id":id}, {'$set':json_body})

        if result.modified_count > 0:
            modified_doc = db.songs.find_one({'id':id})
            return json_util.dumps(modified_doc), 201

        else:
            return {"message":"song found, but nothing updated"}, 200

    else:
        return {"message": "song not found"}, 404
    # Angello Gonzalez

@app.route("/song/<int:id>", methods=['DELETE'])
def delete_song(id):
    result = db.songs.delete_one({'id':id})
    if result.deleted_count > 0:
        return {}, 204
    else:
        return {'message': 'song not found'}, 404
    # Angello Gonzalez
