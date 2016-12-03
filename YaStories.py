import requests, os
from bs4 import BeautifulSoup as BS
from TextWalker import *

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))

sources = [
    "http://fedpress.ru/article/1707985",
    "https://ria.ru/society/20161130/1482499467.html",
    "http://tass.ru/ekonomika/3825796",
    "http://izvestia.ru/news/648466"
]


# sources[0]:
def source_0_text():
    html = requests.get(sources[0]).text
    dom = BS(html, 'html.parser')
    contents = list(dom.find('div', attrs={'class': 'article-box'}).find_all('p'))
    content = ''
    for c in contents:
        content += ' ' + c.get_text()
    return content


# sources[1]:
def source_1_text():
    html = requests.get(sources[1]).text
    dom = BS(html, 'html.parser')
    contents = list(dom.find('div', attrs={'class': 'b-article__body'}).find_all('p'))
    content = ''
    for c in contents:
        content += ' '+c.get_text()
    return content


# sources[2]:
def source_2_text():
    html = requests.get(sources[2]).text
    dom = BS(html, 'html.parser')
    contents = list(dom.find('div', attrs={'class': 'b-material-text__l'}).find_all('p'))
    content = ''
    for c in contents:
        content += ' ' + c.get_text()
    return content


# sources[3]:
def source_3_text():
    html = requests.get(sources[3]).text
    dom = BS(html, 'html.parser')
    contents = list(dom.find('div', attrs={'class': 'text_block'}).find_all('p'))
    content = ''
    for c in contents:
        content += ' ' + c.get_text()
    return content


words_listlist = [
    TextWalker.get_words(source_0_text()),
    TextWalker.get_words(source_1_text()),
    TextWalker.get_words(source_2_text()),
    TextWalker.get_words(source_3_text())
]

commons = sorted(TextWalker.get_commons(words_listlist))
symdiff = sorted(TextWalker.get_symdiff(words_listlist))
nonunique_symdiff = sorted(TextWalker.get_nonunique_symdiff(words_listlist))

with open(SCRIPT_DIR+"\\commons.txt", "w") as f:
    f.writelines('\n'.join(commons))
with open(SCRIPT_DIR+"\\symdiff.txt", "w") as f:
    f.writelines('\n'.join(symdiff))
with open(SCRIPT_DIR + "\\nonunique_symdiff.txt", "w") as f:
    f.writelines('\n'.join(nonunique_symdiff))
