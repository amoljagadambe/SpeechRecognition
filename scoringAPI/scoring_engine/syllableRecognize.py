import os
import sys
import argparse
import util
import pyphen
import pickle
import dtw
from psxDecoder import get_psxDecoder, get_audio_transcribe, get_whole_phoneme, cmuPhonemeDict

_decoder = get_psxDecoder()
_phone_dict = cmuPhonemeDict()


def load_mapDict():
    data_path = 'phDic.cfg'
    with open(data_path, "rb") as f:
        data = pickle.load(f)
    return data


def get_syllables(word):
    dic = pyphen.Pyphen(lang='en')
    res_array = dic.inserted(word)
    # print(res_array)
    return res_array


def find_element_in_list(ele, my_list):
    indices = [i for i, x in enumerate(my_list) if x == ele]
    return indices


def get_mapping_syllable(word):
    syllables = get_syllables(word)
    # all_phonemes = get_whole_phoneme(word)
    all_phonemes = _phone_dict.get_phonemes(word)
    print('syllable: {}'.format(syllables))

    cur_phoneme = all_phonemes[0]
    print('phoneme: {}'.format(cur_phoneme))

    phoneme_list = str(cur_phoneme).strip().split(' ')
    syllable_list = syllables.strip().split('-')
    if len(syllable_list) == 1:
        return [0], [phoneme_list], syllables
    # mapping
    mp_dict = load_mapDict()
    virt_phonemes = []
    for ch in word:
        virt_phonemes.append(mp_dict[ch][0])
    # print(virt_phonemes)
    dtw_path = dtw.get_DTW_path(phoneme_list, virt_phonemes)
    # print(dtw_path)

    res_indices = []
    word_length = len(word)
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
    return res_indices, res_phonemes, syllables


def syllable_recognize(file_path, word):
    res_file = 'test_syllable_shan.txt'
    with open(res_file, 'at') as fp:
        fp.write('file name: {}\n'.format(os.path.basename(file_path)))

        # """
        align_result = util.get_mfa_aligning(file_path, word)
        syll_indices, syll_list, sylls = get_mapping_syllable(word)
        time_frames = []
        if len(align_result) > 0:
            fp.write('syllable: {}\n'.format(sylls))
            for i, syll_ind in enumerate(syll_indices):
                if i < len(syll_indices) - 1:
                    syl_rep = ' '.join([x for x in syll_list[i]])
                    st_time = align_result[syll_ind][0]
                    ed_time = align_result[syll_indices[i+1]-1][1]
                else:
                    syl_rep = ' '.join([x for x in syll_list[-1]])
                    st_time = align_result[syll_ind][0]
                    ed_time = align_result[-1][1]
                time_frames.append([syl_rep, st_time, ed_time])
                fp.write('{}: [{}, {}]\n'.format(syl_rep, st_time, ed_time))
        else:
            _, comp_align_result = get_audio_transcribe(_decoder, file_path)
            for seg in comp_align_result:
                align_result.append([seg[1], seg[2], seg[0]])

        fp.write('\n')

        _, align_result2 = get_audio_transcribe(_decoder, file_path)
        print(align_result2)
        a = 0
        """
        fp.write('phoneme aligning:\n')
        for seg in align_result1:
            fp.write('\t{}: [{:.2f}, {:.2f}]\n'.format(seg[0], seg[1], seg[2]))
        fp.write('\n')
        for seg in align_result2:
            fp.write('\t{}: [{:.2f}, {:.2f}]\n'.format(seg[0], seg[1], seg[2]))
         
        syllables = get_syllables(word)
        fp.write('syllable: {}\n'.format(syllables))

        all_phonemes = get_whole_phoneme(word)
        for ind in range(len(all_phonemes)):
            fp.write('phoneme-{}: {}\n'.format(ind + 1, ' '.join(x for x in all_phonemes[ind])))
        fp.write('\n')
        # """


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Running Aligner Inference")
    parser.add_argument('--dir', default=None, help='Path to data directory which includes sample files')
    args = parser.parse_args()

    work_folder = args.dir
    if work_folder is not None:
        if not os.path.exists(work_folder):
            print("data path error!")
            sys.exit(1)

        conv_folder = os.path.join(work_folder, 'conv_data')
        if not os.path.exists(conv_folder):
            os.mkdir(conv_folder)
        util.convert2wav_folder(work_folder, conv_folder)

        for f in os.listdir(conv_folder):
            print('\nprocessing with {}'.format(f))
            file_path = os.path.join(conv_folder, f)
            # file name:  speaker_word_revision
            word = f.split('-')[1].lower()
            syllable_recognize(file_path, word)
            # get_mapping_syllable(word)
    else:
        print("argument error")
        sys.exit(1)
