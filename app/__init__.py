from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    from .models import Bucketlist, User, BucketlistItem

    @app.route('/bucketlists/', methods=['POST', 'GET'])
    def bucketlists():
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    status = str(request.data.get('completion_status', '')).strip()
                    status_bool = status.lower() == 'true'
                    if name:
                        if Bucketlist.is_name_exists(name, user_id):
                            response = jsonify({
                                'message': 'the name has been used before',
                                'status': 'error'
                            })
                            response.status_code = 400
                            return response
                        bucketlist = Bucketlist(name=name, status=status_bool, created_by=user_id)
                        bucketlist.save()
                        response = jsonify({
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': user_id,
                            'completion_status': bucketlist.completion_status,
                        })

                        return make_response(response), 201

                else:
                    # GET all the bucketlists created by this user
                    bucketlists = Bucketlist.query.filter_by(created_by=user_id)
                    results = []

                    for bucketlist in bucketlists:
                        obj = {
                            'id': bucketlist.id,
                            'name': bucketlist.name,
                            'date_created': bucketlist.date_created,
                            'date_modified': bucketlist.date_modified,
                            'created_by': bucketlist.created_by,
                            'completion_status': bucketlist.completion_status
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401


    @app.route('/bucketlists/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_manipulation(id, **kwargs):
        # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()

                if not bucketlist:
                    # Raise an HTTPException with a 404 not fo``und status code
                    abort(404)

                if request.method == 'DELETE':
                    bucketlist.delete()
                    return {
                               "message": "bucketlist {} deleted successfully".format(bucketlist.id)
                           }, 200

                elif request.method == 'PUT':
                    name = str(request.data.get('name', '')).strip()
                    status = str(request.data.get('completion_status', '')).strip()
                    status_bool = status.lower() == 'true'
                    if name:
                        if Bucketlist.is_name_exists_except_id(name, id, user_id):
                            response = jsonify({
                                'message': 'the name has been used before',
                                'status': 'error'
                            })
                            response.status_code = 400
                            return response
                        bucketlist.name = name
                    if status:
                        bucketlist.completion_status = status_bool
                    bucketlist.save()
                    response = jsonify({
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'completion_status': bucketlist.completion_status,
                        'created_by': bucketlist.created_by
                    })
                    response.status_code = 200
                    return response
                else:
                    # GET
                    response = jsonify({
                        'id': bucketlist.id,
                        'name': bucketlist.name,
                        'date_created': bucketlist.date_created,
                        'date_modified': bucketlist.date_modified,
                        'completion_status': bucketlist.completion_status,
                        'created_by': bucketlist.created_by
                    })
                    response.status_code = 200
                    return response
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    @app.route('/bucketlists/<int:id>/items/', methods=['POST', 'GET'])
    def bucketlist_item(id):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()
                if not bucketlist:
                    response = jsonify({
                        'message': f'The bucketlist with this ID: {id} does not exist',
                        'status': 'error'
                    })
                    response.status_code = 404
                    return response

                if request.method == "POST":
                    name = str(request.data.get('name', ''))
                    status = str(request.data.get('completion_status', '')).strip()
                    status_bool = status.lower() == 'true'
                    if name:
                        if BucketlistItem.is_name_exists(name, id):
                            response = jsonify({
                                'message': 'the name has been used before',
                                'status': 'error'
                            })
                            response.status_code = 400
                            return response
                        bucketlist_item = BucketlistItem(name=name, status=status_bool, bucketlist_id=id)
                        bucketlist_item.save()
                        response = jsonify({
                            'id': bucketlist_item.id,
                            'name': bucketlist_item.name,
                            'date_created': bucketlist_item.date_created,
                            'date_modified': bucketlist_item.date_modified,
                            'bucketlist_id': id,
                            'completion_status': bucketlist_item.completion_status,
                        })

                        return make_response(response), 201
                    else:
                        response = jsonify({
                            'message': 'Please enter a bucketlist item name',
                            'status': 'error'
                        })
                        response.status_code = 404
                        return response

                else:
                    # GET all the bucketlists created by this user
                    bucketlist_items = BucketlistItem.query.filter_by(bucketlist_id=id)
                    results = []

                    for bucketlist_item in bucketlist_items:
                        obj = {
                            'id': bucketlist_item.id,
                            'name': bucketlist_item.name,
                            'date_created': bucketlist_item.date_created,
                            'date_modified': bucketlist_item.date_modified,
                            'bucketlist_id': bucketlist_item.bucketlist_id,
                            'completion_status': bucketlist_item.completion_status,

                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/bucketlists/<int:id>/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
    def bucketlist_item_manipulation(id, item_id, **kwargs):
        # get the access token from the authorization header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Get the user id related to this access token
            user_id = User.decode_token(access_token)

            if not isinstance(user_id, str):
                # If the id is not a string(error), we have a user id
                # Get the bucketlist with the id specified from the URL (<int:id>)
                bucketlist = Bucketlist.query.filter_by(id=id, created_by=user_id).first()

                if not bucketlist:
                    response = jsonify({
                        'message': f'The bucketlist with this ID: {id} does not exist',
                        'status': 'error'
                    })
                    response.status_code = 404
                    return response

                bucketlist_item = BucketlistItem.query.filter_by(id=item_id, bucketlist_id=id).first()
                if not bucketlist_item:
                    response = jsonify({
                        'message': f'The bucketlist item with this ID: {item_id} does not exist',
                        'status': 'error'
                    })
                    response.status_code = 404
                    return response

                if request.method == 'DELETE':
                    bucketlist_item.delete()
                    return {
                               "message": "bucketlist item {} deleted successfully".format(bucketlist_item.id)
                           }, 200

                elif request.method == 'PUT':
                    name = str(request.data.get('name', '')).strip()
                    status = str(request.data.get('completion_status', '')).strip()
                    status_bool = status.lower() == 'true'

                    if name:
                        if BucketlistItem.is_name_exists_except_id(name, item_id, id):
                            response = jsonify({
                                'message': 'the name has been used before',
                                'status': 'error'
                            })
                            response.status_code = 400
                            return response
                        bucketlist_item.name = name
                    if status:
                        bucketlist_item.completion_status = status_bool
                    bucketlist_item.save()
                    response = jsonify({
                        'id': bucketlist_item.id,
                        'name': bucketlist_item.name,
                        'date_created': bucketlist_item.date_created,
                        'date_modified': bucketlist_item.date_modified,
                        'completion_status': bucketlist_item.completion_status,
                        'bucketlist_id': bucketlist_item.bucketlist_id
                    })
                    response.status_code = 200
                    return response
                else:
                    # GET
                    response = jsonify({
                        'id': bucketlist_item.id,
                        'name': bucketlist_item.name,
                        'date_created': bucketlist_item.date_created,
                        'date_modified': bucketlist_item.date_modified,
                        'completion_status': bucketlist_item.completion_status,
                        'bucketlist_id': bucketlist_item.bucketlist_id
                    })
                    response.status_code = 200
                    return response
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                # return an error response, telling the user he is Unauthorized
                return make_response(jsonify(response)), 401

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app


"""- ensure that when creating a new bucket list item, you don't allow creating the bucket list item if there is one 
that already exists with the same name

- also do not allow modifying an item to a name that is already held by another item

- ensure that when making a put request and someone sends json where the key name is missing, you give them the correct 
message

- write tests for the above functionality both for Post and Put requests

- write tests for ensuring the key name is present in the json data during a post or put request

- add a boolean field that shows whether a bucket list item has been completed or not. Add it to the database.
Ensure that it can changed through put requests.
When creating a new bucket list item, that "completed" property is false by default

- add tests for this new functionality"""

"""import os
from flask_script import Manager # class for handling a set of commands
from flask_migrate import Migrate, MigrateCommand
from app import db, create_app, models



app = create_app(config_name=os.getenv('APP_SETTINGS'))
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()"""
