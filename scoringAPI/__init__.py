from flask import Flask
from flask_cors import CORS
from flask_restplus import Api

app = Flask(__name__)
CORS(app)

app.config.from_envvar('APP_SETTINGS')

api = Api(app, title='ScoringAPI-ML', description='Created by GAIS ', default='Flask', default_label='Controllers',
          validate=False)

from scoringAPI import home