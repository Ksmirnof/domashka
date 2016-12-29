import os, subprocess, json
from flask import Flask, request, render_template

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))
OUT_DIR = "%s\\out\\" % SCRIPT_DIR
MYSTEM_BIN = "%s\\bin\\mystem.exe" % SCRIPT_DIR


def mystem_json(string, encoding='utf-8'):
    cmd = [MYSTEM_BIN, "-ci", "-e", encoding, "--format", "json"]
    out, err = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) \
        .communicate(bytes(string, encoding))
    return out


def get_tokens(text):
    j = json.loads(mystem_json(text).decode('utf-8'))
    tokens = list()
    for tok in j:
        token = dict()
        token.update({'token': tok['text']})
        if 'analysis' in tok.keys():
            token.update({'lemma': tok['analysis'][0]['lex']})
        tokens.append(token)
    return tokens


def get_inserts(tokens):
    p_left = r''
    p_right = r''
    inserts_1 = list(); id_1 = 0
    inserts_2 = list(); wordsNlemmas = list(); id_2 = 0
    for tok in tokens:
        if 'lemma' in tok.keys():
            if (tok['token']+' '+tok['lemma']).lower() not in wordsNlemmas:
                id_2 += 1
                inserts_2.append({'id': id_2, 'word': tok['token'], 'lemma': tok['lemma']})
                wordsNlemmas.append((tok['token']+' '+tok['lemma']).lower())
            id_1 += 1
            inserts_1.append({'id': id_1, 'word': tok['token'], 'p_left': p_left, 'p_right': p_right, 'word_id': id_2})
            p_left = ''
            p_right = ''
        else:
            p_left += tok['token']
    if p_left != '':
        inserts_1[len(inserts_1)-1].update({'p_right': inserts_1[len(inserts_1)-1]['p_right']+p_left})
    output = ''
    for i in inserts_1:
        output += 'INSERT INTO first_table (id, word, p_left, p_right, word_id) VALUES (%i, \'%s\', \'%s\', \'%s\', %i);\n'\
                  % (i['id'], i['word'], i['p_left'].replace('\n', '\\n'), i['p_right'].replace('\n', '\\n'), i['word_id'])
    output += '\n'
    for i in inserts_2:
        output += 'INSERT INTO second_table (id, word, lemma) VALUES (%i, \'%s\', \'%s\');\n'\
                  % (i['id'], i['word'].lower(), i['lemma'].lower())
    return output


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def app_index():
    if 'form_submit' in request.form.keys():
        text = request.form['text_text']
        fname = request.form['text_fname']
        result = get_inserts(get_tokens(text))
        with open(OUT_DIR+fname, 'w') as o:
            o.write(result)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
