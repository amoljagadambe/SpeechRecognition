import os
import sys
import json
from . import util
import pyphen
import pickle
from . import dtw
import time
from .psxDecoder import get_psxDecoder, get_audio_transcribe, cmuPhonemeDict
from .phoneRecognizer import recognize_file
from .accentRecognizer import accent_evaluate_from_seg
from .util import get_tts
import pdb

_decoder = get_psxDecoder()
_phone_dict = cmuPhonemeDict()
result_csv = 'test_scoring.csv'
dir_path = os.getcwd()

def load_mapDict():
    data_path = os.path.join(dir_path, 'scoringAPI/scoring_engine', 'phDic.cfg')
    with open(data_path, 'rb') as f:
        data = pickle.load(f)
    return data


def get_syllables(word_text):
    dic = pyphen.Pyphen(lang='en')
    res_array = dic.inserted(word_text)
    # print(res_array)
    return res_array


def find_element_in_list(ele, my_list):
    indices = [i for i, x in enumerate(my_list) if x == ele]
    return indices


def get_mapping_syllable(text_word):
    syllables = get_syllables(text_word)
    # all_phonemes = get_whole_phoneme(word)
    all_phonemes = _phone_dict.get_phonemes(text_word)
    print('syllable: {}'.format(syllables))

    cur_phoneme = all_phonemes[0]
    print('phoneme: {}'.format(cur_phoneme))

    phoneme_list = str(cur_phoneme).strip().split(' ')
    syllable_list = syllables.strip().split('-')
    if len(syllable_list) == 1:
        return [0], [phoneme_list], syllables, cur_phoneme
    # mapping
    mp_dict = load_mapDict()
    virt_phonemes = []
    for ch in text_word:
        virt_phonemes.append(mp_dict[ch][0])
    # print(virt_phonemes)
    dtw_path = dtw.get_DTW_path(phoneme_list, virt_phonemes)
    # print(dtw_path)

    res_indices = []
    word_length = len(text_word)
    prev_len = 0
    for i in range(len(syllable_list)):
        virt_ind = prev_len
        phoneme_ind = find_element_in_list(virt_ind, dtw_path[1])[0]
        syllable_ind = dtw_path[0][phoneme_ind]
        res_indices.append(syllable_ind)
        prev_len += len(syllable_list[i])
    res_phonemes = []
    for i, ind in enumerate(res_indices):
        if i == len(res_indices) - 1:
            res_phonemes.append([x for x in phoneme_list[ind:]])
        else:
            res_phonemes.append([x for x in phoneme_list[ind:res_indices[i+1]]])
    """
    for syl in res_phonemes:
        print(' '.join([x for x in syl]), end=' - ')
    """
    return res_indices, res_phonemes, syllables, cur_phoneme


def syllable_recognize(filename, file_path, word, customerid):
    result_answer = {}
    result_answer['filename'] = filename
    result_answer['word'] = word
    result_answer['customerid'] = customerid

    # pdb.set_trace()
    align_result = util.get_mfa_aligning(file_path, word, customerid)
    syll_indices, syll_list, sylls, phonemes = get_mapping_syllable(word)

    print('get_mapping_syllable: [{}, {}, {}, {}]'.format(syll_indices, syll_list, sylls, phonemes))

    result_answer['syllable'] = sylls
    result_answer['phonemes'] = phonemes
    time_frames = []
    if len(align_result) > 0:
        print('syllable: {}'.format(sylls))
        for i, syll_ind in enumerate(syll_indices):
            if i < len(syll_indices) - 1:
                syl_rep = ' '.join([x for x in syll_list[i]])
                st_time = align_result[syll_ind][0]
                ed_time = align_result[syll_indices[i+1]-1][1]
            else:
                syl_rep = ' '.join([x for x in syll_list[-1]])
                st_time = align_result[syll_ind][0]
                ed_time = align_result[-1][1]
            time_frames.append([syl_rep, sylls.split('-')[i], st_time, ed_time])
            print('{}: [{}, {}]'.format(syl_rep, st_time, ed_time))
        result_answer['timemapping'] = time_frames
    else:
        _, comp_align_result = get_audio_transcribe(_decoder, file_path)
        for seg in comp_align_result:
            align_result.append([seg[1], seg[2], seg[0]])
        result_answer['timemapping'] = align_result
    print("here is the debugger now")
    _, recog_phoneme, phoneme_score = recognize_file(_decoder, file_path, word)
    result_answer['Phoneme-score'] = phoneme_score
    result_answer['extracted-phoneme'] = recog_phoneme
    print('results --> {}: {}]'.format(phoneme_score, recog_phoneme))

    # get Syllable score
    temp_folder = dir_path + '/scoringAPI/scoring_engine/temp'
    #if os.path.exists(temp_folder):
    #    os.system('rm -rf {}'.format(temp_folder))
    #os.mkdir(temp_folder)
    tts_file = get_tts(temp_folder, word, 0)
    tts_align = util.get_mfa_aligning(tts_file, word, customerid)
    if len(tts_align) == 0:
        result_answer['error']="fail2--"
        return result_answer  # result_answer
    tts_timemapping = []
    for i, syll_ind in enumerate(syll_indices):
        if i < len(syll_indices) - 1:
            st_time = tts_align[syll_ind][0]
            ed_time = tts_align[syll_indices[i + 1] - 1][1]
        else:
            st_time = tts_align[syll_ind][0]
            ed_time = tts_align[-1][1]
        tts_timemapping.append([st_time, ed_time])

    syll_scores = []
    for i in range(len(syll_indices)):
        # tts_seg = tts_timemapping[i]
        # user_seg = time_frames[i][-2:]
        # sc = accent_evaluate_from_seg(file_path, user_seg, tts_file, tts_seg)
        std_sylls = ' '.join(x for x in syll_list[i])
        sc1 = util.text_partial_matching(recog_phoneme, std_sylls)
        # syll_scores.append(int((sc+sc1)/2))
        syll_scores.append(int(sc1))
    result_answer['syllables-score'] = syll_scores
    print('result_answer --> {}]'.format(syll_scores))
    return result_answer


def validate_filename(filename):
    # filename:  <speaker>-<word>-<revision>
    speaker, word, revision = '', '', ''
    segments = str(filename).split('-')
    if len(segments) != 3:
        print('Invalid file name: {}'.format(filename))
        return speaker, word, revision
    speaker = segments[0]
    word = segments[1].lower()
    revision = segments[2][:-4]
    return speaker, word, revision


def word_score(word, filename, voice_file, customerid):
    # convert file
    cv_filename = voice_file[:-4] + '_conv.wav'
    print("right from here")
    print(filename)
    print(word)
    print(cv_filename)
    if not util.convert_file(voice_file, cv_filename):
        return 'Fail1-'
    # _, word, _ = validate_filename(f)
    time1 = float(round(time.time()))

    # pdb.set_trace()
    results = syllable_recognize(filename, cv_filename, word, customerid)
    time2 = float(round(time.time()))
    delta_time = time2 - time1
    if results is None or results['error'] != '':
        res = json.dumps({"audio-file": filename,
                          "word": word,
                          "word-phoneme": results["phonemes"],
                          "user-phoneme": results["extracted-phoneme"],
                          "syllable": results["syllable"],
                          "score": results["Phoneme-score"],
                          "error": results["error"],
                          "processing-time": delta_time})
        return res

    # result JSON
    tm_mapping = []
    sc_list = []
    for seg in results['timemapping']:
        tm_mapping.append(json.dumps({"syllable": str(seg[1]).upper(),
                                "start-time": seg[2],
                                "end-time": seg[3]}))
        # tmp_str = '{}: [{} - {}]'.format(seg[1], seg[2], seg[3])
        sc_list.append(seg[1])
    syll_score_list = []
    for i, seg in enumerate(results["syllables-score"]):
        if int(seg) >= 90:
            syll_score_list.append(json.dumps({"Syllable": str(sc_list[i]).upper(),
                                               "score": "BEST"}))
        elif int(seg) >= 75:
            syll_score_list.append(json.dumps({"Syllable": str(sc_list[i]).upper(),
                                               "score": "GOOD"}))
        else:
            syll_score_list.append(json.dumps({"Syllable": str(sc_list[i]).upper(),
                                               "score": "BAD"}))
    res = json.dumps({"audio-file": filename,
                      "word": word,
                      "phoneme": results["phonemes"],
                      "syllable": results["syllable"],
                      "score": results["Phoneme-score"],
                      "syllable-timeframe": tm_mapping,
                      "syllable-score": syll_score_list,
                      "processing-time": delta_time})

    try:
        os.remove(cv_filename)
    except:
        pass
    return res

