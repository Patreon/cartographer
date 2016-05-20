#!flask/bin/python
from cartographer.serializers import JSONAPICollectionSerializer
from flask import jsonify, abort, request, Blueprint
from generic_social_network.app import db

from generic_social_network.app.models.query_builders.people_dbm import PeopleDBM
from generic_social_network.app.resources.people_resource import PeopleSerializer, PeopleParser

people_blueprint = Blueprint('people_blueprint', __name__)
people_dbm = PeopleDBM(db)


@people_blueprint.route('/people/<int:person_id>', methods=['POST', 'GET', 'PUT', 'DELETE'])
def route_person(person_id):
    if request.method == 'POST':
        return create_person(request, person_id)
    elif request.method == 'PUT':
        return update_person(request, person_id)
    elif request.method == 'DELETE':
        return delete_person(person_id)
    else:
        return read_person(person_id)


@people_blueprint.route('/people', methods=['POST', 'GET'])
def route_people():
    if request.method == 'POST':
        return create_person(request, None)
    else:
        return list_people(request)


def read_person(person_id):
    person = get_person_or_404(person_id)
    return success_with_person(person)


def list_people(request_):
    return jsonify(JSONAPICollectionSerializer([
        PeopleSerializer(
            person,
            inbound_request=request_
        )
        for person in people_dbm.all()
    ]).as_json_api_document())


def delete_person(person_id):
    person = get_person_or_404(person_id)
    people_dbm.delete(person_id=person_id)
    return success_with_person(person)


def update_person(request_, person_id):
    def person_found_behavior(person):
        if person is None:
            abort(404)

    json = validate_inbound_person(request_, person_id, person_found_behavior)

    people_dbm.update_from_json(json)
    return read_person(json['person_id'])


def create_person(request_, person_id):
    def person_found_behavior(person_):
        if person_ is not None:
            abort(409, '{0} with id {1} already exists'.format('person', person_id))

    json = validate_inbound_person(request_, person_id, person_found_behavior)

    people_dbm.create_from_json(json)
    person = people_dbm.find_by_id(json['person_id'])
    return success_with_person(person), 201


def get_person_or_404(person_id):
    person = people_dbm.find_by_id(person_id)
    if person is None:
        abort(404)
    return person


def validate_inbound_person(request_, person_id, person_found_behavior):
    try:
        table_data = PeopleParser(inbound_request=request_).validated_table_data()
    except Exception as e:
        abort(400, ', '.join(e.args))
    table_data = standardize_person_ids_or_abort(table_data, person_id)
    person_id = table_data['person_id']
    person = people_dbm.find_by_id(person_id)
    person_found_behavior(person)
    return table_data


def standardize_person_ids_or_abort(json, person_id):
    if json is None:
        json = {}
    if 'person_id' in json:
        if person_id != json['person_id']:
            abort(400, 'Provided person object had a id that did not match the provided route')
    elif person_id:
        json['person_id'] = person_id
    return json


def success_with_person(person):
    return jsonify(PeopleSerializer(person).as_json_api_document())
