import pyphen
import sys


def get_syllables(word):
    dic = pyphen.Pyphen(lang='en')
    res_array = dic.inserted(word)
    return res_array


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('argument error:')
        print('python get_syllable.py <word>')
        sys.exit(1)

    text = sys.argv[1]
    sylls = get_syllables(text)
    print("word: {}\tsyllable: {}".format(text, sylls))

