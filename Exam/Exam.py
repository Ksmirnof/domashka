import os, subprocess, json, re


SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))

MYSTEM_BIN = "%s\\bin\\mystem.exe" % SCRIPT_DIR
WORDS_TXT = "%s\\data\\adyghe-unparsed-words.txt" % SCRIPT_DIR
PAGE_HTML = "%s\\data\\page.html" % SCRIPT_DIR

OUT_WORDLIST = "%s\\out\\wordlist.txt" % SCRIPT_DIR
OUT_RUSNOUNS = "%s\\out\\rus_nouns.txt" % SCRIPT_DIR
OUT_SQL = "%s\\out\\sql.txt" % SCRIPT_DIR


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleanr = re.compile('[{}|=,\.!?\'\":_\\\/0-9\u2026\u00ab\u00bb]')
    cleantext = re.sub(cleanr, '', cleantext)
    return cleantext


def mystem_json(string, encoding='utf-8'):
    cmd = [MYSTEM_BIN, "-ni", "-e", encoding, "--format", "json"]
    out, err = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) \
        .communicate(bytes(string, encoding))
    return out


def n1():
    with open(WORDS_TXT, 'rb') as w:
        with open(PAGE_HTML, 'rb') as h:
            with open(OUT_WORDLIST, 'w') as o:
                lines = w.read().decode('utf-8').splitlines()
                html = clean_html(h.read().decode('utf-8')).lower()
                split_html = html.split()
                for l in lines:
                    if l.lower() in split_html:
                        o.write(l+'\n')


def n2n3():
    with open(WORDS_TXT, 'rb') as w:
        with open(OUT_RUSNOUNS, 'w') as o_r:
            with open(OUT_SQL, 'w') as o_s:
                lines = mystem_json(w.read().decode('utf-8')).splitlines()
                for l in lines:
                    j = json.loads(l.decode('utf-8'))
                    text = j['text']
                    analysis = j['analysis']
                    o_r_written = False
                    o_s_lex = []
                    for a in analysis:
                        grlist = a['gr'].split(',')
                        if 'S' in grlist and 'ед' in grlist and ('им' in grlist or 'од=им' in grlist or 'неод=им' in grlist):
                            if not o_r_written:
                                o_r.write(text+'\n')
                                o_r_written = True
                            if a['lex'] not in o_s_lex:
                                o_s.write(
                                    "INSERT INTO rus_words (wordform, lemma) VALUES('%s', '%s');\n"
                                    % (text, a['lex'])
                                )
                                o_s_lex.append(a['lex'])

n1()
n2n3()
