import flask
from flask import jsonify, request
from . import db_session
from .tasks import Tasks


blueprint = flask.Blueprint('news_api', __name__, template_folder='templates')


@blueprint.route('/check_task/<int:id>')
def check(id):
    db_sess = db_session.create_session()
    items = db_sess.query(Tasks)
    return jsonify(
        {
            'tasks': [item.to_dict(only=('title', 'content', 'id'))
                      for item in items]
        }
    )
