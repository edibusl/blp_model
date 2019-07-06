import db_manager
from orm import Base
from flask import Flask
from gw_endpoints import bp_endpoints


def create_db(db_filename=None):
    db_manager.init(db_filename)
    Base.metadata.create_all(db_manager.engine)


def start_flask():
    app = Flask(__name__)
    app.register_blueprint(bp_endpoints)

    return app
