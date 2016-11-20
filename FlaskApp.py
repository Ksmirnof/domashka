import os
import json
from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)
dir_path = os.path.dirname(os.path.realpath(__file__))


@app.route('/', methods=['GET', 'POST'])
def app_index():
    message = ''
    if 'form_submit' in request.form.keys():
        data = {
            'lang': request.form['text_lang'],
            'red_color': request.form['text_red'],
            'green_color': request.form['text_green'],
            'blue_color': request.form['text_blue']
        }
        with open(dir_path+'/data.json', 'a+') as f:
            f.seek(0)
            t = f.read()
            try:
                j = json.loads(t)
            except json.decoder.JSONDecodeError:
                j = {'info': []}
            j['info'].append(data)
            f.truncate(0)
            json.dump(j, f)
        message = 'Saved!'
    return render_template('index.html', message=message)


@app.route('/stats')
def app_stats():
    try:
        with open(dir_path + '/data.json', 'r') as f:
            try:
                j = json.load(f)
            except json.decoder.JSONDecodeError:
                j = {'info': []}
    except:
        j = {'info': []}

    info = j['info']

    count_submit = len(info)

    langs = []
    for i in info:
        if i['lang'] not in langs:
            langs.append(i['lang'])
    count_diff_lang = len(langs)

    red_names = {}
    for i in info:
        if i['red_color'] in red_names.keys():
            red_names.update({i['red_color']: red_names[i['red_color']] + 1})
        else:
            red_names.update({i['red_color']: 1})
    try:
        popname_red_color = max(red_names.items(), key=lambda x: x[1])[0]
    except:
        popname_red_color = ''

    green_names = {}
    for i in info:
        if i['green_color'] in green_names.keys():
            green_names.update({i['green_color']: green_names[i['green_color']] + 1})
        else:
            green_names.update({i['green_color']: 1})
    try:
        popname_green_color = max(green_names.items(), key=lambda x: x[1])[0]
    except:
        popname_green_color = ''

    blue_names = {}
    for i in info:
        if i['blue_color'] in blue_names.keys():
            blue_names.update({i['blue_color']: blue_names[i['blue_color']] + 1})
        else:
            blue_names.update({i['blue_color']: 1})
    try:
        popname_blue_color = max(blue_names.items(), key=lambda x: x[1])[0]
    except:
        popname_blue_color = ''

    return render_template(
        'stats.html',
        count_submit=count_submit,
        count_diff_lang=count_diff_lang,
        popname_red_color=popname_red_color,
        popname_green_color=popname_green_color,
        popname_blue_color=popname_blue_color
    )


@app.route('/json')
def app_json():
    try:
        with open(dir_path + '/data.json', 'r') as f:
            t = f.read()
        return t
    except:
        return ''


@app.route('/search')
def app_search():
    return render_template('search.html')


@app.route('/results', methods=['POST'])
def app_results():
    strs = []
    if 'form_submit' in request.form.keys():
        try:
            with open(dir_path + '/data.json', 'r') as f:
                try:
                    j = json.load(f)
                except json.decoder.JSONDecodeError:
                    j = {'info': []}
        except:
            j = {'info': []}
        info = j['info']
        for i in info:
            if 'cb_red' in request.form.keys(): strs.append('RED: '+i['red_color'])
            if 'cb_green' in request.form.keys(): strs.append('GREEN: '+i['green_color'])
            if 'cb_blue' in request.form.keys(): strs.append('BLUE: '+i['blue_color'])
    return render_template('results.html', strs=strs)


if __name__ == '__main__':
    app.run()
