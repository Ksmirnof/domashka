from collections import Counter
from re import sub


class TextWalker:

    @staticmethod
    def get_words(text):
        return sub("[^\w]", " ", text).split()

    @staticmethod
    def get_commons(words_listlist):
        c_out = Counter(words_listlist[0])
        for words_list in words_listlist:
            c_list = Counter(words_list)
            c_out = c_list & c_out
        return list(c_out)

    @staticmethod
    def get_symdiff(words_listlist):
        commons = TextWalker.get_commons(words_listlist)
        c_out = Counter(words_listlist[0])
        for words_list in words_listlist:
            c_list = Counter(words_list)
            c_out = c_list | c_out
        c_out.subtract(Counter(commons))
        c_out += Counter()
        return list(c_out)

    @staticmethod
    def get_nonunique_symdiff(words_listlist):
        commons = TextWalker.get_commons(words_listlist)
        c_dout = Counter(words_listlist[0])
        c_out = Counter()
        for words_list in words_listlist:
            c_list = Counter(words_list)
            c_dout = c_list | c_dout
        c_dout.subtract(Counter(commons))
        c_dout += Counter()
        for k in c_dout.keys():
            if c_dout[k] > 1:
                c_out[k] = c_dout[k]
        return list(c_out)
