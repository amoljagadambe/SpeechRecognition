from flask_restplus import fields
from scoringAPI import api
from werkzeug.datastructures import FileStorage

user_fields = api.model('wordScoring', {
    'filename': fields.String(required=False),
    'fileloc': fields.String(required=False),
    'customerid': fields.String(required=False),
    'word': fields.String(required=False),


})


upload_parser = api.parser()
upload_parser.add_argument('filename', location='files',type=FileStorage)
# upload_parser.add_argument('voice', location='files',type=FileStorage)
upload_parser.add_argument('word', type=str, help='Should Be Lowercase')