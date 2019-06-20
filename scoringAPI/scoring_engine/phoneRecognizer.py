import os
import sys
import argparse
from . import util
from .psxDecoder import get_psxDecoder, get_audio_transcribe, get_whole_phoneme


def recognize_file(ds, file_path, real_word):
    """
    :param ds: pocketsphinx decoder
    :param file_path: audio file path to be recognized
    :param real_word: transcription of input audio - one word
    :return: phonemes array of real_word, recognized word, score
    """
    try:
        res1, res2 = get_audio_transcribe(ds, file_path)
        result1 = ' '.join(x[0] for x in res1)
        result2 = ' '.join(x[0] for x in res2)
        # print('{}: {}'.format(f, res))

        # correct phone array
        r_phone = get_whole_phoneme(real_word)
        score = 0
        dic_phonemes = ''
        rec_phonemes = ''
        for cur_phoneme in r_phone:
            r_phone_string = ' '.join(y for y in cur_phoneme)

            # score
            if len(r_phone_string) == 0 or len(result1) == 0 or len(result2) == 0:
                sc = 0
            else:
                sc1 = util.text_matching(r_phone_string, result1)
                sc2 = util.text_matching(r_phone_string, result2)
                if sc1 > score:
                    score = sc1
                    dic_phonemes = r_phone_string
                    rec_phonemes = result1
                if sc2 > score:
                    score = sc2
                    dic_phonemes = r_phone_string
                    rec_phonemes = result2
        print('file: {}'.format(os.path.basename(file_path)))
        print('{}: [{}]  <===>  [{}]\t\tscore: {}'.format(real_word, dic_phonemes, rec_phonemes, score))
        return dic_phonemes, rec_phonemes, score
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Running Aligner Inference")
    parser.add_argument('--dir', default=None, help='Path to data directory which includes sample files')
    parser.add_argument('--file', default=None, help='Path to sample file to be tested')
    parser.add_argument('--word', default=None, help='text of word to be tested')

    args = parser.parse_args()

    work_folder = args.dir
    test_file_path = args.file
    word_text = args.word

    if work_folder is not None:
        if not os.path.exists(work_folder):
            print("data path error!")
            sys.exit(1)

        conv_folder = os.path.join(work_folder, 'conv_data')
        if not os.path.exists(conv_folder):
            os.mkdir(conv_folder)
        util.convert2wav_folder(work_folder, conv_folder)

        ds = get_psxDecoder()
        for f in os.listdir(conv_folder):
            file_path = os.path.join(conv_folder, f)
            # file name:  speaker_word_revision
            word = f.split('-')[1].lower()
            # recognize_file(ds, file_path, os.path.basename(f)[:-4])
            recognize_file(ds, file_path, word)
    else:
        if test_file_path is None:
            print("argument error")
            sys.exit(1)
        if word_text is None:
            print("argument error")
            sys.exit(1)
        conv_folder = 'conv_data'
        if not os.path.exists(conv_folder):
            os.mkdir(conv_folder)
        conv_file_path = os.path.basename(test_file_path)[:-4] + '.wav'
        conv_file_path = os.path.join(conv_folder, conv_file_path)
        util.convert_file(test_file_path, conv_file_path)
        ds = get_psxDecoder()
        recognize_file(ds, conv_file_path, word_text)
