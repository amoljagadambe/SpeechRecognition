
import wave
import numpy as np
import os
from os import path
from pocketsphinx.pocketsphinx import *

#BASE_FOLDER = os.path.abspath(os.path.dirname(__name__))
#upload_folder = BASE_FOLDER + '/scoringAPI/'
class cmuPhonemeDict(object):
    def __init__(self, dict_file= 'scoring_engine/model/en-us.dict'):
        self.dict_file = dict_file
        self.dict = {}
        self.load_dict()

    def load_dict(self):
        for line in open(self.dict_file, 'rt').readlines():
            split_idx = line.find(' ')
            self.dict[line[0:split_idx]] = line[split_idx + 1:-1]

    def get_phonemes(self, word):
        try:
            word_phone = self.dict[word.lower()]
            oth_word = word.lower()+'(2)'
            if oth_word in self.dict.keys():
                return [word_phone, self.dict[oth_word]]
            return [word_phone]
        except:
            return []


class psxDecoder(object):

    def __init__(self, MODEL_DIR):
        #print(MODEL_DIR)
        self.config = Decoder.default_config()
        try:
            self.config.set_string('-hmm', os.path.join(MODEL_DIR, 'en-us'))
            self.config.set_string('-allphone', os.path.join(MODEL_DIR, 'en-us-phone.lm.bin'))
            self.config.set_string('-backtrace', 'yes')
            self.config.set_float('-beam', 10e-57)
            self.config.set_float('-wbeam', 10e-56)
            # self.config.set_float('-maxhmmpf', -1)
            self.config.set_float('-lw', 2.0)
            # self.config.set_float('-kws_threshold', 1e+20)
            #self.config.set_string('-logfn', 'scoring_engine/null')
        except Exception as e:
            print(e)
            return
        self.decoder = Decoder(self.config)

    def decode(self, data):
        self.decoder.start_utt()
        self.decoder.process_raw(data, False, True)
        self.decoder.end_utt()

    def get_dec_result(self):
        dec_sentence = []
        for seg in self.decoder.seg():
            seg = seg.word
            if seg == '<s>' or seg == '</s>':
                continue
            if seg == '<sil>':
                continue
            elif seg == '[NOISE]':
                continue
            if '(' in seg:
                seg = str(seg).split('(')[0]
            dec_sentence.append(seg)

        return ' '.join(seg for seg in dec_sentence)

    def get_spotting(self):
        if self.decoder.hyp() is not None:
            result_list = []
            # print(self.decoder.hyp().hypstr)
            for s in self.decoder.seg():
                seg = s.word
                if seg == '<s>' or seg == '</s>':
                    continue
                elif 'sil' in seg.lower():
                    continue
                elif '+' in seg:
                    continue
                elif seg == '[NOISE]':
                    continue
                if '(' in seg:
                    seg = str(seg).split('(')[0]

                result_list.append([seg, s.start_frame / 100., s.end_frame / 100.])
            return result_list
        return []


def get_audio_transcribe(decoder, audio_file):
    fin = wave.open(audio_file, 'rb')
    fs = fin.getframerate()
    if fs != 16000:
        print("samplerate error!")
        return []
    else:
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

    ex_audio = list(audio)
    sil_tm = 0.2  # 0.2 seconds
    frames = int(fs * sil_tm)
    for i in range(frames):
        ex_audio.insert(0, audio[0])
        ex_audio.append(audio[-1])
    ex_audio = np.array(ex_audio)
    fin.close()

    data = np.array(ex_audio).tobytes()
    decoder.decode(data)
    res1 = decoder.get_spotting()
    for i in range(len(res1)):
        res1[i][1] -= sil_tm
        res1[i][2] -= sil_tm

    data = np.array(audio).tobytes()
    decoder.decode(data)
    res2 = decoder.get_spotting()
    return res1, res2


def get_whole_phoneme(word):
    word = word.lower()
    with open('scoring_engine/model/en-us.dict', 'rt') as dict:
        all_phone = []
        for d_word in dict:
            d_word = d_word.strip()
            pre_word = d_word.split(' ')[0]
            phonemes = d_word.split(' ')[1:]
            if pre_word == word:
                all_phone.append(phonemes)
            else:
                pre_word = pre_word.replace('(', '')
                pre_word = pre_word.replace(')', '')
                if pre_word[:-1] == word and pre_word[-1].isdigit():
                    all_phone.append(phonemes)

    return all_phone


def get_psxDecoder():
    #print(upload_folder)
    return psxDecoder('scoring_engine/model')

