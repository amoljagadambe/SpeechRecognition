import os
import sys
import getpass
import shutil
from fuzzywuzzy import fuzz
import librosa
import scipy.io.wavfile as wav
from scipy.fftpack import fft
import numpy
from . import parse_TextGrid
from gtts import gTTS


def get_tts(dir, text, index):

    if index == 0:
        tts_file = '{}.mp3'.format(os.path.join(dir, text))
    else:
        tts_file = '{}_{}.mp3'.format(os.path.join(dir, text), index)

    tts_file = '{}.mp3'.format(os.path.join(dir, text))
    wav_file = tts_file[:-4] + '.wav'

    if not os.path.exists(tts_file):
        tts = gTTS(text=text, lang='en')
        tts.save(tts_file)
        convert_file(tts_file, wav_file)

    return wav_file


def convert_file(src_file, dst_file):
    convert_cmd = 'ffmpeg -i \"{}\" -acodec pcm_s16le -ac 1 -ar 16000 \"{}\" -y -loglevel panic'.format(
        src_file,
        dst_file)
    try:
        os.system(convert_cmd)
        return True
    except Exception as error:
        print(error)
        return False


def convert2wav_folder(src_folder, dst_folder):
    for file_name in os.listdir(src_folder):
        if file_name.lower().endswith('.mp3') or file_name.lower().endswith('.wav'):
            org_file_path = os.path.join(src_folder, file_name)
            new_filename = file_name[:-4] + '.wav'
            new_file_path = os.path.join(dst_folder, new_filename)
            if os.path.exists(new_file_path):
                continue
            convert_file(org_file_path, new_file_path)


def text_matching(text1, text2):
    test1 = str(text1).lower()
    test2 = str(text2).lower()
    rate = fuzz.ratio(test1, test2)
    return rate


def text_partial_matching(text1, text2):
    test1 = str(text1).lower()
    test2 = str(text2).lower()
    rate = fuzz.partial_ratio(test1, test2)
    return rate


def read_audio_librosa(wav_path):
    if not os.path.exists(wav_path):
        print("cannot find wave file!")
        return [], -1
    return librosa.load(wav_path, sr=16000)


def read_audio_wav(wav_path):
    if not os.path.exists(wav_path):
        print("cannot find wave file!")
        return -1, []
    return wav.read(wav_path)


def stF0Raw(fs, frame):
    chunk = len(frame)
    # Take the fft and square each value
    fftData = abs(numpy.fft.rfft(frame)) ** 2
    # find the maximum
    which = fftData[1:].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData) - 1:
        y0, y1, y2 = numpy.log(fftData[which - 1:which + 2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which + x1) * fs / chunk
    else:
        thefreq = which * fs / chunk
    return thefreq


def stNewFeature(signal, Fs, Win, Step):
    Win = int(Win)
    Step = int(Step)

    # Signal normalization
    signal = numpy.double(signal)

    signal = signal / (2.0 ** 15)
    DC = signal.mean()
    MAX = (numpy.abs(signal)).max()
    signal = (signal - DC) / (MAX + 0.0000000001)

    N = len(signal)  # total number of samples
    curPos = 0
    nFFT = int(Win / 2)

    I0 = 0.000001
    stFeatures = []
    while (curPos + Win - 1 < N):  # for each short-term window until the end of signal
        x = signal[curPos:curPos + Win]  # get current window
        curPos = curPos + Step  # update window position
        X = abs(fft(x))  # get fft magnitude
        X = X[0:nFFT]  # normalize fft
        X = X / len(X)

        curFV = stF0Raw(Fs, x)  # pitch: f0-raw
        stFeatures.append(curFV)

    return stFeatures


def get_pitch(wave_file):
    if not os.path.exists(wave_file):
        print('Error! Audio file does not exist!')
        return None

    wav_data, sample_rate = read_audio_librosa(wave_file)
    frame_len = int(0.10 * sample_rate)
    frame_step = int(0.01 * sample_rate)
    pitch = stNewFeature(wav_data, sample_rate, frame_len, frame_step)
    return numpy.array(pitch)


def get_pitch_level(nInitial, nFinal, nMainPos, nMain):
    nLevel = 0
    # initial
    if nInitial < -6.0:
        nLevel += 1
    elif nInitial < -2.0:
        nLevel += 2
    elif nInitial < 2.0:
        nLevel += 3
    elif nInitial < 6.0:
        nLevel += 4
    else:
        nLevel += 5
    nLevel *= 10

    # main saliency
    if nMain < -6.0:
        nLevel += 1
    elif nMain < -2.0:
        nLevel += 2
    elif nMain < 2.0:
        nLevel += 3
    elif nMain < 6.0:
        nLevel += 4
    else:
        nLevel += 5
    nLevel *= 10

    # final
    if nFinal < -6.0:
        nLevel += 1
    elif nFinal < -2.0:
        nLevel += 2
    elif nFinal < 2.0:
        nLevel += 3
    elif nFinal < 6.0:
        nLevel += 4
    else:
        nLevel += 5
    nLevel *= 10

    # time position of main saliency(accent)
    if nMainPos < 1 / 4:
        nLevel += 1
    elif nMainPos < 2 / 4:
        nLevel += 2
    elif nMainPos < 3 / 4:
        nLevel += 3
    else:
        nLevel += 4
    pitchLevel = nLevel
    return pitchLevel


def get_mfa_aligning(wave_file, word_text):
    if not os.path.exists(wave_file):
        print("wave file does not exist.")
        return None

    import getpass
    home_dir = 'home/hp'
    tmp_dir = os.path.join(home_dir, 'Documents/MFA')
    os.system("rm -rf {}".format(tmp_dir))

    src_folder = os.path.join('scoring_engine', 'aligner', 'data')
    out_folder = os.path.join('scoring_engine', 'aligner', 'out')
    if os.path.exists(src_folder):
        os.system('rm -rf {}'.format(src_folder))
    os.mkdir(src_folder)

    if os.path.exists(out_folder):
        os.system('rm -rf {}'.format(out_folder))

    text_filename = os.path.basename(wave_file)[:-4] + '.lab'
    text_filepath = os.path.join(src_folder, text_filename)
    if os.path.exists(text_filepath):
        try:
            os.remove(text_filepath)
        except:
            pass
    with open(text_filepath, 'wt') as lab:
        lab.write(str(word_text))
    shutil.copy(wave_file, os.path.join(src_folder, os.path.basename(wave_file)))

    bin_path = os.path.join('scoring_engine', 'aligner', 'bin', 'mfa_align')
    lexi_path = os.path.join('scoring_engine', 'aligner', 'pretrained_models', 'lexicon.txt')
    # cmds = '{} {} {} english {}'.format(bin_path, src_folder, lexi_path, out_folder)
    cmds = "{} {} {} english {}".format(bin_path, src_folder, lexi_path, out_folder)
    try:
        os.system(cmds)
    except Exception as e:
        print(e)

    grid_filename = os.path.basename(wave_file)[:-4] + '.TextGrid'
    grid_filepath = os.path.join('scoring_engine', 'aligner', os.path.basename(out_folder), grid_filename)
    if os.path.exists(grid_filepath):
        segments = parse_TextGrid.read_TextGrid(grid_filepath)
    else:
        segments = []
    return segments


def get_mfa_aligning_from_sentence(wave_file, text):
    src_folder = os.path.join('scoring_engine', 'aligner', 'data')
    out_folder = os.path.join('scoring_engine', 'aligner', 'out')
    if os.path.exists(src_folder):
        os.system('rm -rf {}'.format(src_folder))
    os.mkdir(src_folder)

    if os.path.exists(out_folder):
        os.system('rm -rf {}'.format(out_folder))

    username = getpass.getuser()
    home_dir = os.environ['HOME']
    tmp_dir = os.path.join(home_dir, 'Documents', 'MFA')
    if os.path.exists(tmp_dir):
        os.system('rm -rf {}'.format(tmp_dir))

    text_filename = os.path.basename(wave_file)[:-4] + '.lab'
    text_filepath = os.path.join(src_folder, text_filename)
    if os.path.exists(text_filepath):
        try:
            os.remove(text_filepath)
        except:
            pass
    with open(text_filepath, 'wt') as lab:
        lab.write(str(text))
    shutil.copy(wave_file, os.path.join(src_folder, os.path.basename(wave_file)))

    bin_path = os.path.join('scoring_engine', 'aligner', 'bin', 'mfa_align')
    lexi_path = os.path.join('scoring_engine', 'aligner', 'pretrained_models', 'lexicon.txt')
    # cmds = '{} {} {} english {}'.format(bin_path, src_folder, lexi_path, out_folder)
    cmds = "{} {} {} english {}".format(bin_path, src_folder, lexi_path, out_folder)
    try:
        os.system(cmds)
    except Exception as e:
        print(e)

    grid_filename = os.path.basename(wave_file)[:-4] + '.TextGrid'
    grid_filepath = os.path.join('scoring_engine', 'aligner', os.path.basename(out_folder), grid_filename)
    if os.path.exists(grid_filepath):
        segments = parse_TextGrid.read_sentence_TextGrid(grid_filepath)
    else:
        segments = [[], []]
    return segments


def trim_audio_ffmpeg(src_file, start_tm, end_tm, dst_file):
    if not os.path.exists(src_file):
        return
    if os.path.exists(dst_file):
        os.remove(dst_file)
    commands = 'ffmpeg  -i \"{}\" -ss {:.2f} -to {:.2f} \"{}\" -y -loglevel panic'.format(
        src_file, start_tm, end_tm, dst_file)
    os.system(commands)
    return dst_file
