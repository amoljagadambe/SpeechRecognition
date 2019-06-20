import os
import json
from . import util
from . import dtw
import time
from .syllableScoring import find_element_in_list
from .psxDecoder import get_psxDecoder, get_audio_transcribe, cmuPhonemeDict
_phone_dict = cmuPhonemeDict()
_decoder = get_psxDecoder()
result_file = 'word_alignment.csv'


def parse_filename(filename):
    name, text, id_num = '', '', -1
    segments = filename.split('_')
    if len(segments) != 3:
        return name, text, id_num
    name = str(segments[0])
    words = segments[1].lower().split('-')
    text = ' '.join(x for x in words)
    id_num = segments[2][:-4]
    if not id_num.isdigit():
        id_num = -1
    return name, text, id_num


def filter_sentence_by_punctuation(text):
    import re
    line = re.sub('[,!@#$]', '', text)
    return line


def get_word_score(sentence, audio_file):
    words_list = sentence.split(' ')
    phonemes_list = []
    word_phonemes = []
    ind_list = []
    for wrd in words_list:
        p_array = _phone_dict.get_phonemes(wrd)
        if len(p_array) == 0:
            ind_list.append(0)
            word_phonemes.append(p_array)
            continue
        word_phonemes.append(p_array[0])
        p_list = p_array[0].split(' ')
        ind_list.append(len(p_list))
        phonemes_list.extend(p_list)

    # get phonemes from audio
    real_phonemes_list = []
    _, comp_align_result = get_audio_transcribe(_decoder, audio_file)
    for seg in comp_align_result:
        real_phonemes_list.append(seg[0])

    dtw_path = dtw.get_DTW_path(phonemes_list, real_phonemes_list)
    prev_len = 0
    prev_ind = 0
    words_scores = []
    for i in range(len(ind_list)):
        if i < len(ind_list)-1:
            if ind_list[i] == 0:
                words_scores.append(0)
                continue
            virt_ind = prev_len + ind_list[i] - 1
            prev_len += ind_list[i]
            std_ind = find_element_in_list(virt_ind, dtw_path[0])[-1]
            utter_ind = dtw_path[1][std_ind]
            utter_phoneme = ' '.join(x for x in real_phonemes_list[prev_ind:utter_ind+1])
            sc = util.text_matching(word_phonemes[i], utter_phoneme)
            words_scores.append(sc)
            prev_ind = utter_ind+1
        else:
            utter_phoneme = ' '.join(x for x in real_phonemes_list[prev_ind:])
            sc = util.text_matching(word_phonemes[i], utter_phoneme)
            words_scores.append(sc)

    res_scores = []
    for i, sc in enumerate(words_scores):
        if sc >= 80:
            res_scores.append([words_list[i], 'BEST'])
        elif sc >= 50:
            res_scores.append([words_list[i], 'GOOD'])
        else:
            res_scores.append([words_list[i], 'BAD'])
    return res_scores


def word_aligning(audio_file, text):
    [word_mapping, phoneme_mapping] = util.get_mfa_aligning_from_sentence(audio_file, text)
    word_list = text.split(' ')
    assert len(word_mapping) == len(word_list)
    for i, word in enumerate(word_list):
        if word_mapping[i][2] != word:
            word_mapping[i][2] = word
    return word_mapping


def sentence_scoring(filename, file_path, sentence):
    # convert file
    cv_filename = file_path[:-4] + '_conv.wav'
    if not util.convert_file(file_path, cv_filename):
        return 'Fail3-'

    # file name:  <speaker name>_<sentence>_<iteration>
    sentence = filter_sentence_by_punctuation(sentence)

    mili1 = float(round(time.time()))
    wrd_align = word_aligning(cv_filename, sentence)

    # get score by word
    word_scores = get_word_score(sentence, cv_filename)

    mili2 = float(round(time.time()))
    delta_time = mili2 - mili1

    words_list = []
    for x in wrd_align:
        words_list.append(json.dumps({"word": x[2],
                                      "start-time": x[0],
                                      "end-time": x[1]}))
    score_list = []
    for x in word_scores:
        score_list.append(json.dumps({"word": x[0],
                                      "score": x[1]}))

    res = json.dumps({"audio-file": filename,
                      "sentence": sentence,
                      "word-timeframe": words_list,
                      "word-score": score_list,
                      "processing-time": delta_time})
    try:
        os.remove(cv_filename)
    except:
        pass
    return res

