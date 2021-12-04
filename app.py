import json
import logging
import sys
import os

from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint, google
#import database_services.RDBService as d_service
from flask_login import (LoginManager, UserMixin,
                         current_user, login_user, logout_user)

from application_services.address_resource import addressResource as a_service
from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.movie_history_resource import movieHistoryResource as h_service
from application_services.user_resource import userResource as u_service
from database_services.RDBService import RDBService as d_service
from middleware.notification import Notifications
from middleware.simple_security import Security

app = Flask(__name__)
CORS(app)

sec = Security()
userSNSTopic = Notifications()
app.secret_key = "my secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'google.login'

gb = sec.get_google_blueprint()
app.register_blueprint(gb, url_prefix="/login")

@app.before_request
def before_request():
    print("before_request is running!")
    print("request.path:", request.path)

    # a_ok = sec.check_authentication(request.path)
    # print("a_ok:", a_ok)
    # if a_ok[0] != 200:
    #     session["next_url"] = request.base_url
    #     return redirect(url_for('google.login'))


@app.after_request
def after_request(response):
    path = request.path
    method = request.method
    body = request.get_json()
    SNS_response = userSNSTopic.check_user_notif(path, method, body, response)
    return response


@app.route('/')
def hello_world():
    next_url = session.get("next_url", None)
    if next_url:
        session.pop("next_url", None)
        return redirect(next_url)
    return 'Hello Patis World! Welcome to the USER API'


@app.route('/imdb/artists/<prefix>')
def get_artists_by_prefix(prefix):
    res = IMDBArtistResource.get_by_name_prefix(prefix)
    rsp = Response(json.dumps(res), status=200, content_type="application/json")
    return rsp


@app.route('/<db_schema>/<table_name>/<column_name>/<prefix>')
def get_by_prefix(db_schema, table_name, column_name, prefix):
    res = d_service.get_by_prefix(db_schema, table_name, column_name, prefix)
    rsp = Response(json.dumps(res), status=200, content_type="application/json")
    return rsp


@app.route('/users', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        res = u_service.get_all_users()
        if not res:
            rsp = Response("USERS NOT FOUND", status=200, content_type='text/plain')
            return rsp

        u_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'POST':
        try:
            body = request.get_json()
            res = u_service.add_user(body)
            location = "/users/" + str(res[1])
            statusRespDict = {
                "status": "201 CREATED",
                "location": location
            }
            rsp = Response(json.dumps(statusRespDict), status=201, content_type="application/json")
            return rsp
        except Exception as e:
            print(e)
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

@app.route('/users/<userID>', methods=['GET', 'PUT', 'DELETE'])
def get_users_by_id(userID):
    if request.method == 'GET':
        res = u_service.get_user_by_id(userID)
        if not res:
            rsp = Response("USER NOT FOUND", status=200, content_type='text/plain')
            return rsp
        u_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'PUT':
        try:
            body = request.get_json()
            res = u_service.update_user(userID, body)
            if not res:
                rsp = Response("USER NOT FOUND", status=200, content_type='text/plain')
                return rsp
            location = "/users/" + userID
            statusRespDict = {
                "status": "200 UPDATED",
                "location": location
            }
            rsp = Response(json.dumps(statusRespDict), status=200, content_type='application/json')
            return rsp
        except Exception as e:
            print(e)
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    elif request.method == 'DELETE':
        try:
            res = u_service.delete_user(userID)
            if not res:
                rsp = Response("USER NOT FOUND", status=200, content_type='text/plain')
                return rsp
            rsp = Response("OK DELETE", status=204, content_type='text/plain')
            return rsp
        except Exception as e:
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp


@app.route('/users/<userID>/address', methods=['GET'])
def get_address_by_user(userID):
    if request.method == 'GET':
        res = u_service.get_address_by_user("user_service", "user", "address", userID)
        if not res:
            rsp = Response("ADDRESS NOT FOUND", status=200, content_type='text/plain')
            return rsp
        u_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp


@app.route('/addresses', methods=['GET', 'POST'])
def get_addresses():
    if request.method == 'GET':
        res = a_service.get_all_addresses()
        if not res:
            rsp = Response("ADDRESS NOT FOUND", status=200, content_type='text/plain')
            return rsp
        a_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'POST':
        logging.info("in post")
        try:
            body = request.get_json(force=True)
            res = a_service.add_address(body)
            if res:
                location = "/addresses/" + str(res[1])
                statusRespDict = {
                    "status": "201 CREATED",
                    "location": location
                }
                rsp = Response(json.dumps(statusRespDict), status=201, content_type="application/json")
                return rsp
            else:
                rsp = Response("UNPROCESSABLE ENTITY", status=422, content_type='text/plain')
                return rsp
        except Exception as e:
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp


@app.route('/addresses', methods=['GET','PUT', 'DELETE'])
def get_addresses_by_id(addressID):
    if request.method == 'GET':
        res = a_service.get_address_by_id(addressID)
        if not res:
            rsp = Response("ADDRESS NOT FOUND", status=200, content_type='text/plain')
            return rsp
        a_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'PUT':
        try:
            body = request.get_json()
            res = a_service.update_address(addressID, body)
            if res:
                location = "/addresses/" + addressID
                statusRespDict = {
                    "status": "200 UPDATED",
                    "location": location
                }
                rsp = Response(json.dumps(statusRespDict), status=200, content_type='application/json')
                return rsp
            else:
                rsp = Response("ADDRESS NOT FOUND", status=200, content_type='text/plain')
                return rsp
        except Exception as e:
            print(str(e))
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    elif request.method == 'DELETE':
        try:
            res = a_service.delete_address(addressID)
            if not res:
                rsp = Response("ADDRESS NOT FOUND", status=200, content_type='text/plain')
                return rsp
            rsp = Response("OK DELETE", status=204, content_type='text/plain')
            return rsp
        except Exception as e:
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

@app.route('/addresses/<addressID>/users', methods=['GET'])
def get_users_by_address(addressID):
    if request.method == 'GET':
        res = a_service.get_user_by_address(addressID)
        if not res:
            rsp = Response("ADDRESS OR USERS NOT FOUND", status=200, content_type='text/plain')
            return rsp
        u_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp


@app.route('/movie-histories', methods=['GET', 'POST'])
def get_movie_histories():
    if request.method == 'GET':
        res = h_service.get_all_history()
        if not res:
            rsp = Response("HISTORIES NOT FOUND", status=200, content_type='text/plain')
            return rsp
        h_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'POST':
        try:
            body = request.get_json()
            h_service.add_history(body)
            print(body)
            location = "/movie-histories/" + str(body['userID']) + "/" + str(body['movieID'])
            statusRespDict = {
                "status": "201 CREATED",
                "location": location
            }
            rsp = Response(json.dumps(statusRespDict), status=201, content_type="application/json")
            return rsp
        except Exception as e:
            print(e)
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp


@app.route('/movie-histories/user/<userID>', methods=['GET'])
def get_history_by_user_id(userID):
    if request.method == 'GET':
        res = h_service.get_history_by_user_id(userID)
        if not res:
            rsp = Response("HISTORY NOT FOUND", status=200, content_type='text/plain')
            return rsp
        h_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

@app.route('/movie-histories/movie/<movieID>', methods=['GET'])
def get_history_by_movie_id(movieID):
    if request.method == 'GET':
        res = h_service.get_history_by_movie_id(movieID)
        if not res:
            rsp = Response("HISTORY NOT FOUND", status=200, content_type='text/plain')
            return rsp
        h_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

@app.route('/movie-histories/<userID>/likedMovies', methods=['GET'])
def get_liked_movie_history_by_user_id(userID):
    if request.method == 'GET':
        res = h_service.get_liked_movies(userID)
        if not res:
            rsp = Response("HISTORY NOT FOUND", status=200, content_type='text/plain')
            return rsp
        h_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

@app.route('/movie-histories/<userID>/<movieID>', methods=['GET', 'DELETE'])
def get_history_by_user_movie_id(userID, movieID):
    if request.method == 'GET':
        res = h_service.get_history_by_user_movie_id(userID, movieID)
        if not res:
            rsp = Response("HISTORY NOT FOUND", status=200, content_type='text/plain')
            return rsp
        h_service.get_links(res)
        rsp = Response(json.dumps(res), status=200, content_type="application/json")
        return rsp
    elif request.method == 'DELETE':
        try:
            res = h_service.delete_history_by_user_movie_id(userID, movieID)
            if not res:
                rsp = Response("HISTORY NOT FOUND", status=200, content_type='text/plain')
                return rsp
            rsp = Response("OK DELETE", status=204, content_type='application/json')
            return rsp
        except Exception as e:
            print(str(e))
            statusRespDict = {
                "status": "422 UNPROCESSABLE ENTITY",
                "error message": str(e)
            }
            rsp = Response(json.dumps(statusRespDict), status=422, content_type='application/json')
            return rsp
    else:
        rsp = Response("NOT IMPLEMENTED", status=400)
        return rsp

if __name__ == '__main__':
    app.run(host="0.0.0.0")
