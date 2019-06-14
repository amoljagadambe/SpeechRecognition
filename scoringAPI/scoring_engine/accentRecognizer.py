import os
from . import util
import numpy
import math
from .util import get_tts


def accent_evaluate_from_file(work_folder, wave_file, word):
    ind = int(os.path.basename(wave_file).split('-')[-1][0])
    tts_wave_file = get_tts(work_folder, word, ind)
    pitch0 = util.get_pitch(tts_wave_file)
    pitch1 = util.get_pitch(wave_file)
    return get_accent_score(pitch0, pitch1)


def accent_evaluate_from_seg(file1, seg1, file2, seg2):
    new_file1 = util.trim_audio_ffmpeg(file1, seg1[0], seg1[1], 'temp1.wav')
    new_file2 = util.trim_audio_ffmpeg(file2, seg2[0], seg2[1], 'temp2.wav')
    pitch0 = util.get_pitch(new_file1)
    pitch1 = util.get_pitch(new_file2)
    return get_accent_score(pitch0, pitch1)


def get_accent_score(pit0, pit1):
    if len(pit0) == 0 and len(pit1) == 0:
        return 100
    elif len(pit0) == 0 or len(pit1) == 0:
        return 0
    nInitial0 = max(1, numpy.where(pit0 > 0)[0][0])
    nFinal0 = max(1, numpy.where(pit0 > 0)[0][-1])
    localPos0 = numpy.argmax(pit0)
    aver0 = max(1, numpy.mean(pit0))
    localMax0 = max(1, numpy.max(pit0))

    nInitial0 = float(12.0 * math.log2(float(nInitial0 / aver0)))
    nFinal0 = float(12.0 * math.log2(float(nFinal0 / aver0)))
    nMainPos0 = float(localPos0 - len(pit0))
    nMain0 = float(12.0 * math.log2(float(localMax0 / aver0)))

    accentLevel0 = util.get_pitch_level(nInitial0, nFinal0, nMainPos0, nMain0)

    nInitial1 = max(1, numpy.where(pit1 > 0)[0][0])
    nFinal1 = max(1, numpy.where(pit1 > 0)[0][-1])
    localPos1 = numpy.argmax(pit1)
    aver1 = max(1, numpy.mean(pit1))
    localMax1 = max(1, numpy.max(pit1))

    nInitial1 = float(12.0 * math.log2(nInitial1 / aver1))
    nFinal1 = float(12.0 * math.log2(nFinal1 / aver1))
    nMainPos1 = float(localPos1 - len(pit1))
    nMain1 = float(12.0 * math.log2(localMax1 / aver1))

    accentLevel1 = util.get_pitch_level(nInitial1, nFinal1, nMainPos1, nMain1)

    sc = util.text_matching(str(accentLevel0), str(accentLevel1))
    print('accent score: {}'.format(sc))
    return sc

