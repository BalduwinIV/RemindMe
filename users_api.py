from flask import Blueprint, request, jsonify
from data import db_session
from data.users import *


blueprint = Blueprint('users_api', __name__, template_folder='templates')


@blueprint.route('/api/users', methods=["GET"])
def get_users():
    session = db_session.create_session()
    users = session.query(User).all()
    return jsonify({
        'users': [item.to_dict(only=('id', 'username')) for item in users]
    })


@blueprint.route('/api/users/check_password', methods=["POST"])
def check_password():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['username', 'password']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    user = session.query(User).filter(User.username == request.json['username']).first()
    if not user:
        return jsonify({'error': 'Not found'})
    if user.check_password(request.json['password']):
        return jsonify({'success': 'OK'})
    return jsonify({'success': 'NO'})


@blueprint.route('/api/users/', methods=["POST"])
def add_user():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['username', 'password']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    new_user = User()
    new_user.username = request.json['username']
    new_user.set_password(request.json['password'])
    session.add(new_user)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=["GET"])
def get_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify({
        'user': user.to_dict(only=('id', 'username'))
    })


@blueprint.route('/api/users/<int:user_id>', methods=["PUT"])
def edit_user(user_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id)
    if not user.first():
        return jsonify({'error': 'Not found'})
    try:
        user.update(request.json)
    except Exception:
        return jsonify({'error': 'Wrong arguments'})
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=["DELETE"])
def delete_user(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    session.delete(user)
    session.commit()
    return jsonify({'success': 'OK'})