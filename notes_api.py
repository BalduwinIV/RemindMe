from flask import Blueprint, jsonify, request
from data import db_session
from data.users import *


blueprint = Blueprint('notes_api', __name__, template_folder='templates')


@blueprint.route('/api/notes', methods=["GET"])
def get_notes():
    session = db_session.create_session()
    notes = session.query(Notes).all()
    return jsonify({
        'notes': [item.to_dict(only=('id', 'title', 'content')) for item in notes]
    })


@blueprint.route('/api/notes/', methods=["POST"])
def create_note():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in ['title', 'content']):
        return jsonify({'error': 'Bad request'})
    session = db_session.create_session()
    new_note = Notes()
    new_note.title = request.json['title']
    new_note.content = request.json['content']
    session.add(new_note)
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/notes/<int:note_id>', methods=["GET"])
def get_note(note_id):
    session = db_session.create_session()
    note = session.query(Notes).get(note_id)
    if not note:
        return jsonify({'error': 'Not found'})
    return jsonify({
        'note': note.to_dict(only=('id', 'title', 'content'))
    })


@blueprint.route('/api/notes/<int:note_id>', methods=["PUT"])
def edit_note(note_id):
    if not request.json:
        return jsonify({'error': 'Empty request'})
    session = db_session.create_session()
    note = session.query(Notes).filter(Notes.id == note_id)
    if not note.first():
        return jsonify({'error': 'Not found'})
    try:
        note.update(request.json)
    except Exception:
        return jsonify({'error': f'Wrong arguments'})
    session.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/notes/<int:note_id>', methods=["DELETE"])
def delete_note(note_id):
    session = db_session.create_session()
    note = session.query(Notes).get(note_id)
    if not note:
        return jsonify({'error': 'Not found'})
    session.delete(note)
    session.commit()
    return jsonify({'success': 'OK'})