import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def show_drinks():
    # print(jwt)
    all_drinks = Drink.query.all()
    print(all_drinks)
    drinks = []
    for drink in all_drinks:
        drinks.append(drink.short())
    print(drinks)
    return jsonify({"success": True, "drinks": drinks})

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    print('payload', payload)

    drinks = []
    all_drinks = Drink.query.all()
    print('all_drinks:', all_drinks)
    for drink in all_drinks:
        drinks.append(drink.long())
    print('drinks:', drinks)
    return jsonify({"success": True, "drinks": drinks})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def create_drink(payload):
    body = request.get_json()
    # return body
    print('body:', body)
    
    title = body.get("title", None)
    print('title', title) 
    recipe = json.dumps(body.get("recipe", None))
    print('recipe:', recipe)
    if title is None or recipe is None:
        abort(400)
    else:
        drink = ' '

        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()
        print('new_drink:', new_drink.long())

        # drink.append(new_drink.long())
        # print('drink:', drink)

    return jsonify({"success": True, "drinks": new_drink.long()})

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(id, payload):

    body = request.get_json()

    drink = Drink.query.filter_by(id=id).one_or_none()

    if drink is None:
        abort(404)
    
    title = body.get['title']
    recipe = json.dumps(body.get['recipe'])
    drink.title = title
    drink.recipe = recipe

    drink.update()

    updated_drink = [drink.long()]

    return jsonify({"success": True, "drinks": updated_drink})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id, payload):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)

    drink.delete()
    return jsonify({"success": True, "delete": id})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401
    
@app.errorhandler(403)
def forbidden_access(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden Access"
    }), 403

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response