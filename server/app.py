#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Campers(Resource):

    def get(self):
        campers = Camper.query.all()
        response_data = [camper.to_dict_no_signups() for camper in campers]
        response = make_response(
            response_data,
            200
        )
        return response
    
    def post(self):
        try:
            json_data = request.get_json()
            if not json_data or 'name' not in json_data or 'age' not in json_data:
                return {'errors': 'Invalid JSON data. Please provide "name" and "age" fields.'}, 400

            name = json_data.get('name')
            age = json_data.get('age')

            new_record = Camper(name=name, age=age)
            db.session.add(new_record)
            db.session.commit()

            response_dict = new_record.to_dict()

            return response_dict, 201
        except Exception as e:
            return {'errors': str(e)}, 400
        
class Campers_by_id(Resource):

    def get(self, id):
        try:
            if not Camper.query.filter_by(id=id).first():
                return {'error': 'Camper not found'}, 404
            else:
                response_dict = Camper.query.filter_by(id=id).first().to_dict()

                response = make_response(
                    response_dict,
                    200,
                )

                return response
        except Exception as e:
            return {'error': str(e)}, 422
    
    def patch(self, id):

        try:
            json_data = request.get_json()
            if not json_data or 'name' not in json_data or 'age' not in json_data:
                return {'errors': ['validation errors']}, 400
            elif not json_data.get('name'):
                return {'errors': ['validation errors']}, 400
            
            record = Camper.query.filter_by(id=id).first()
            if not record:
                return {'error': 'Campher not found'}, 404
            
            for attr in json_data:
                setattr(record, attr, json_data.get(attr))
            
            db.session.add(record)
            db.session.commit()

            response_dict = record.to_dict()

            return response_dict, 202
        except Exception as e:
            return {'errors': ["validation errors"]}, 400
    
class Activities(Resource):

    def get(self):
        activities = Activity.query.all()
        response_data = [activity.to_dict() for activity in activities]
        response = make_response(
            response_data,
            200
        )
        return response

class Activities_by_id(Resource):

    def delete(self, id):
        if not Activity.query.filter_by(id=id).first():
            return {'error': 'Activity not found'}, 404
        record = Activity.query.filter_by(id=id).first()
        db.session.delete(record)
        db.session.commit()

        response_dict = {'message': 'record successfully deleted'}
        response = make_response(   
            response_dict,
            204
        )
        return response

class Signups(Resource):

    def post(self):
        try:
            json_data = request.get_json()
            if not json_data or 'camper_id' not in json_data or 'activity_id' not in json_data or 'time' not in json_data:
                return {"errors": ["validation errors"]}, 400
            
            time = json_data.get('time')
            camper_id = json_data.get('camper_id')
            activity_id = json_data.get('activity_id')

            new_record = Signup(time=time, camper_id=camper_id, activity_id=activity_id)
            print(new_record)
            db.session.add(new_record)
            db.session.commit()

            response_dict = new_record.to_dict()
            return response_dict, 201
        except Exception as e:
            return {"errors": ["validation errors"]}, 400


api.add_resource(Campers, '/campers', endpoint='campers')
api.add_resource(Campers_by_id, '/campers/<int:id>', endpoint='campers_id')
api.add_resource(Activities, '/activities', endpoint='activities')
api.add_resource(Activities_by_id, '/activities/<int:id>', endpoint='activities_id')
api.add_resource(Signups, '/signups', endpoint='signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
