import os
import re
import json
from collections import OrderedDict


def remove_empty_lines(text):
    """remove empty lines"""
    assert len(text) > 0
    assert isinstance(text, list)
    text = [t.strip() for t in text]
    if b'' in text:
        text.remove(b'')
    return text


class TextGrid(object):
    def __init__(self, text):
        self.text = text
        self.line_count = 0
        self._get_type()
        self._get_time_intval()
        self._get_size()
        self.tier_list = []
        self._get_item_list()

    def _extract_pattern(self, pattern, inc):
        try:
            group = re.match(pattern, self.text[self.line_count].decode("utf-8")).group(1)
            self.line_count += inc
        except AttributeError:
            raise ValueError("File format error at line %d:%s" % (self.line_count, self.text[self.line_count]))
        return group

    def _get_type(self):
        self.file_type = self._extract_pattern(r"File type = \"(.*)\"", 2)

    def _get_time_intval(self):
        self.xmin = self._extract_pattern(r"xmin = (.*)", 1)
        self.xmax = self._extract_pattern(r"xmax = (.*)", 2)

    def _get_size(self):
        self.size = int(self._extract_pattern(r"size = (.*)", 2))

    def _get_item_list(self):
        """Only supports IntervalTier currently"""
        for itemIdx in range(1, self.size + 1):
            tier = OrderedDict()
            item_list = []
            tier_idx = self._extract_pattern(r"item \[(.*)\]:", 1)
            tier_class = self._extract_pattern(r"class = \"(.*)\"", 1)
            if tier_class != "IntervalTier":
                raise NotImplementedError("Only IntervalTier class is supported currently")
            tier_name = self._extract_pattern(r"name = \"(.*)\"", 1)
            tier_xmin = self._extract_pattern(r"xmin = (.*)", 1)
            tier_xmax = self._extract_pattern(r"xmax = (.*)", 1)
            tier_size = self._extract_pattern(r"intervals: size = (.*)", 1)
            for i in range(int(tier_size)):
                item = OrderedDict()
                item["idx"] = self._extract_pattern(r"intervals \[(.*)\]", 1)
                item["xmin"] = self._extract_pattern(r"xmin = (.*)", 1)
                item["xmax"] = self._extract_pattern(r"xmax = (.*)", 1)
                item["text"] = self._extract_pattern(r"text = \"(.*)\"", 1)
                item_list.append(item)
            tier["idx"] = tier_idx
            tier["class"] = tier_class
            tier["name"] = tier_name
            tier["xmin"] = tier_xmin
            tier["xmax"] = tier_xmax
            tier["size"] = tier_size
            tier["items"] = item_list
            self.tier_list.append(tier)

    def toJson(self):
        _json = OrderedDict()
        _json["file_type"] = self.file_type
        _json["xmin"] = self.xmin
        _json["xmax"] = self.xmax
        _json["size"] = self.size
        _json["tiers"] = self.tier_list
        return json.dumps(_json, ensure_ascii=False, indent=2).encode("utf-8")

    def get_phoneme_list(self):
        for tier in self.tier_list:
            if tier['name'] != 'phones':
                continue
            result = []
            for seg in tier['items']:
                xmin = float(seg['xmin'])
                xmax = float(seg['xmax'])
                word = seg['text']
                if word in ['sil', 'sp', '']:
                    continue
                result.append([xmin, xmax, word])
            return result

    def get_word_list(self):
        for tier in self.tier_list:
            if tier['name'] != 'words':
                continue
            result = []
            for seg in tier['items']:
                xmin = float(seg['xmin'])
                xmax = float(seg['xmax'])
                word = seg['text']
                if word == '':
                    continue
                result.append([xmin, xmax, word])
            return result


def read_gridfile(grid_file):
    tsv_list = []
    with open(grid_file) as f:
        for i in range(14):
            f.readline()
        while f.readline():
            st = f.readline().strip()
            st = st.split(' = ')[-1]

            if st.replace('\"', '') == "IntervalTier":
                break

            ed = f.readline().strip()
            ed = ed.split(' = ')[-1]
            word = f.readline().strip()
            word = word.split(' = ')[-1]
            word = word.replace('\"', '')

            if word == '':
                continue
            else:
                line = [float(st), float(ed), word]
                tsv_list.append(line)

        f.close()
    return tsv_list


def read_TextGrid(grid_file):
    tsv_list = []
    if not os.path.exists(grid_file):
        return tsv_list
    with open(grid_file) as f:
        while True:
            tmp = f.readline().strip()
            if 'name = \"phones\"' in tmp:
                break
        for i in range(3):
            f.readline()
        while f.readline():
            st = f.readline().strip()
            st = st.split(' = ')[-1]

            if st.replace('\"', '') == "IntervalTier":
                break

            ed = f.readline().strip()
            ed = ed.split(' = ')[-1]
            word = f.readline().strip()
            word = word.split(' = ')[-1]
            word = word.replace('\"', '')

            if word == '' or word == 'sil' or word == 'sp':
                continue
            else:
                line = [float(st), float(ed), word]
                tsv_list.append(line)

    return tsv_list


def read_sentence_TextGrid(grid_file):
    with open(grid_file, "rb") as f:
        text = f.readlines()
    if len(text) == 0:
        raise IOError("input textgrid file can't be empty")
    text = remove_empty_lines(text)
    textgrid = TextGrid(text)

    wrd_list = textgrid.get_word_list()
    phoneme_list = textgrid.get_phoneme_list()
    return wrd_list, phoneme_list


if __name__ == '__main__':
    grid_file = os.path.join('aligner', 'out', 'data', 'Ashish_Each-gumball-costs-one-dime_1.TextGrid')
    with open(grid_file, "rb") as f:
        text = f.readlines()
    if len(text) == 0:
        raise IOError("input textgrid file can't be empty")
    text = remove_empty_lines(text)
    textgrid = TextGrid(text)

    wrd_list = textgrid.get_word_list()
    with open('json_test', "wb") as f:
        f.write(textgrid.toJson())
