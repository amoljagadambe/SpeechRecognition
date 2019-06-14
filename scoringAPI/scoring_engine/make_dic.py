import cPickle as pickle

my_dict = {}
my_dict['a'] = ['AH', 'AE', 'AH', 'AO', 'AW', 'AY']
my_dict['b'] = ['B']
my_dict['c'] = ['K', 'CH']
my_dict['d'] = ['D', 'DH']
my_dict['e'] = ['IY', 'IH', 'EH', 'ER', 'EY']
my_dict['f'] = ['F']
my_dict['g'] = ['G']
my_dict['h'] = ['HH']
my_dict['i'] = ['IY', 'IH']
my_dict['j'] = ['JH']
my_dict['k'] = ['K']
my_dict['l'] = ['L']
my_dict['m'] = ['M']
my_dict['n'] = ['N', 'NG']
my_dict['o'] = ['OW', 'OY']
my_dict['p'] = ['P']
my_dict['q'] = ['K']
my_dict['r'] = ['R']
my_dict['s'] = ['S', 'SH']
my_dict['t'] = ['T', 'TH', 'SH']
my_dict['u'] = ['UH', 'UW']
my_dict['v'] = ['V']
my_dict['w'] = ['W']
my_dict['x'] = ['SH', 'EX']
my_dict['y'] = ['Y']
my_dict['z'] = ['Z', 'ZH']

data_path = 'phDic.cfg'


def save_dic():
    with open(data_path, "wb") as f:
        pickle.dump(my_dict, f)
        f.close()


def read_dic():
    with open(data_path, "rb") as f:
        data = pickle.load(f)
        f.close()
        print(data)


save_dic()
