from scoringAPI.scoring_engine.user_input import user_fields
from scoringAPI.scoring_engine import syllableScoring, word_alignment
from flask_restplus import Resource
from flask import request, json
from scoringAPI import api
import datetime
import random
import json
import os


# set variables
upload_tmp_folder = os.path.join('..', 'scoringAPI', 'uploads')

word_scoring = api.namespace('VoiceProcessor', description='Operations related to word_scoring')


@word_scoring.route('/word_scoring', endpoint='/word_scoring')
class wordScoringApi(Resource):

    @api.expect(user_fields, validate=False)
    def post(self):
        json_obj = request.get_json()
        word = json_obj['word']
        filename = json_obj['filename']
        fileloc = json_obj['fileloc']
        customerid = json_obj['customerid']
        # word_name = request.json()
        # print(word_name)
        # print(type(word_name))
        # f = request.files['voice']
        # filename = f.filename
        # base64_data = f.read()

        # if base64_data is None:
        #     res = json.dumps({"result": "Failed"})
        #
        # tmp_file = word_name + '_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(
        #     random.randint(10000, 99999)) + '.wav'
        # tmp_file_path = os.path.join(upload_tmp_folder, tmp_file)
        #
        # with open(tmp_file_path, 'wb') as fi:
        #     fi.write(base64_data)
        # print('received file: {}'.format(filename))
        # data = {'filename': filename, 'voice': tmp_file_path, 'word': word_name}
        data = {'filename': filename, 'fileloc': fileloc, 'word': word, 'customerid':customerid }
        # filename = data['filename']
        # upload_filename = data['voice']
        # word_name = data['word']

        filename = data['filename']
        upload_filename = data['fileloc']
        word_name = data['word']
        customerid = data['customerid']

        print('server filename, upload_filename, word_name, customerid: [{}, {}, {}, {}]'.
              format(filename, upload_filename, word_name, customerid))

        # print("server filename: {}".format(filename))
        # print("server upload_filename: {}".format(upload_filename))
        # print("server word_name: {}".format(word_name))

        if word_name == '':
            res = json.dumps({"result": "Input word Error!"})
        elif os.path.exists(upload_filename):
            print("processing file: {}".format(upload_filename))
            try:
                import pdb
                pdb.set_trace()
                res = syllableScoring.word_score(str(word_name).lower(), filename, upload_filename, customerid)
                # os.remove(upload_filename)
            except Exception as e:
                print(e)
                res = json.dumps({"result3": res + "& Details : {1}".format(e.errno, e.strerror)})
                # res = json.dumps({"result3": res + " Details "})
        else:
            res = json.dumps({"result": 'Seems File is not found.'})

        return res


sentence_scoring = api.namespace('/VoiceProcessor/sentence_scoring', description='Operations related to sentence_scoring')


@sentence_scoring.route('/VoiceProcessor/sentence_scoring', endpoint="/sentence_scoring")
class sentenceScoringApi(Resource):

    @api.expect(user_fields, validate=False)
    def post(self):
        res = 'Fail5-'
        sentence = request.form.get('sentence')
        f = request.files['voice']
        filename = f.filename
        base64_data = f.read()

        if base64_data is None:
            res = json.dumps({"result": "Failed"})

        tmp_file = 'upload_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(
            random.randint(10000, 99999)) + '.wav'
        tmp_file_path = os.path.join(upload_tmp_folder, tmp_file)

        with open(tmp_file_path, 'wb') as fi:
            fi.write(base64_data)
        print('received file: {}'.format(filename))

        data = {'filename': filename, 'voice': tmp_file_path, 'sentence': sentence}
        filename = data['filename']
        upload_filename = data['voice']
        sentence = data['sentence']

        if sentence == '':
            res = json.dumps({"result": "Input sentence Error!"})
        elif os.path.exists(upload_filename):
            print("processing file: {}".format(upload_filename))
            try:
                res = word_alignment.sentence_scoring(filename, upload_filename, sentence)
            # os.remove(upload_filename)
            except Exception as e:
                print(e)
                res = json.dumps({"result4": res + "Details"})
        else:
            res = json.dumps({"result": 'File is not found..'})

        return res
