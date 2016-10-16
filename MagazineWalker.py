import os, io, subprocess, requests, re, csv
from bs4 import BeautifulSoup as BS
from math import ceil

SCRIPT_DIR, SCRIPT_FILE = os.path.split(os.path.abspath(__file__))
MYSTEM_BIN = "%s\\bin\\mystem.exe" % SCRIPT_DIR


class Crawler:

    MAGAZINE_URL = "http://unecha-gazeta.ru/"
    MAGAZINE_ENCODING = 'cp1251'

    DATA_KEYS = (
        'path',
        'author',
        'sex',
        'birthday',
        'header',
        'created',
        'sphere',
        'genre_fi',
        'type',
        'topic',
        'chronotop',
        'style',
        'audience_age',
        'audience_level',
        'audience_size',
        'source',
        'publication',
        'publisher',
        'publ_year',
        'medium',
        'country',
        'region',
        'language'
    )

    OUTPUT_ROOT_PATH = "%s\\%s\\" % (SCRIPT_DIR, 'газета')
    METADATA_PATH = OUTPUT_ROOT_PATH + '\\' + 'metadata.csv'

    _csv = None

    def __init__(self, need_csv=True):
        if need_csv:
            if not os.path.exists(os.path.split(self.METADATA_PATH)[0]):
                os.makedirs(os.path.split(self.METADATA_PATH)[0])
            self._csv = CSV(self.METADATA_PATH, self.DATA_KEYS)

    def count_links_per_page(self):
        return (requests.get(self.MAGAZINE_URL).text.count("h2") - 2) / 2

    def get_links(self, max_count):
        lpp = self.count_links_per_page()
        pages = ceil(max_count / lpp)
        links = []
        for i in range(pages):
            page_result = requests.get("%s/page/%i" % (self.MAGAZINE_URL, i+1))
            if page_result.status_code == requests.codes.ok:
                dom = BS(page_result.text, 'html.parser')
                for h2 in dom('h2'):
                    if h2.a is not None:
                        links.append(h2.a['href'])
                    if len(links) == max_count:
                        break
        return links

    def get_data(self, link):
        def escape(string):
            return (
                string
                    .replace('\xa0', ' ')
                    .replace('\x85', '...')
                    .replace('\x91', "'")
                    .replace('\x92', "'")
                    .replace('\x93', '"')
                    .replace('\x94', '"')
                    .replace('\x96', '-')
                    .replace('\x97', '-')
            )
        data = {}
        page_result = requests.get(link)
        if page_result.status_code == requests.codes.ok:
            page_result.encoding = self.MAGAZINE_ENCODING
            dom = BS(page_result.text, 'html.parser')

            content = dom.find(id=re.compile('news-id-[0-9]+'))
            data.update({
                'content': escape(content.get_text().strip('\n\r\xa0 '))
            })

            header = dom('div', attrs={'class': 'twhite_content'})[4].h2
            data.update({
                'header': escape(header.get_text().strip('\n\r\xa0 '))
            })

            datelist = re.search(
                'Добавлено: \(([0-9]+-[0-9]+-[0-9]+),.*\)',
                dom('div', attrs={'class': 'twhite_content'})[4].p.get_text()
            ).group(1).split('-')
            date = '.'.join(datelist)
            data.update({'date': date})
            publ_year = datelist[2]
            data.update({'publ_year': publ_year})
            data.update({
                'source': escape(link)
            })
            # static info:
            data.update({
                'sex': '',
                'birthday': '',
                'sphere': 'публицистика',
                'genre_fi': '',
                'type': '',
                'chronotop': '',
                'style': 'нейтральный',
                'audience_age': 'н-возраст',
                'audience_level': 'н-уровень',
                'audience_size': 'районная',
                'publication': 'Унечская газета',
                'publisher': '',
                'medium': 'газета',
                'country': 'Россия',
                'region': 'Брянская область',
                'language': 'ru'
            })
            # can't extract:
            data.update({
                'author': 'Noname',
                'topic': ''
            })
        return data

    def create_files(self, data):
        datelist = data['date'].split('.')
        month = int(datelist[1])
        year = int(datelist[2])
        header = re.sub(r'[\\/*?:"<>|]', "", data['header'])
        src_plain_path = "%s\\plain\\%i\\%i\\%s.txt" % (self.OUTPUT_ROOT_PATH, year, month, header)
        mystem_plain_path = "%s\\mystem-plain\\%i\\%i\\%s.txt" % (self.OUTPUT_ROOT_PATH, year, month, header)
        mystem_xml_path = "%s\\mystem-xml\\%i\\%i\\%s.xml" % (self.OUTPUT_ROOT_PATH, year, month, header)

        if not os.path.exists(os.path.split(src_plain_path)[0]):
            os.makedirs(os.path.split(src_plain_path)[0])
        if not os.path.exists(os.path.split(mystem_plain_path)[0]):
            os.makedirs(os.path.split(mystem_plain_path)[0])
        if not os.path.exists(os.path.split(mystem_xml_path)[0]):
            os.makedirs(os.path.split(mystem_xml_path)[0])

        with io.StringIO(data['content']) as content_io:
            with open(mystem_plain_path, 'wb') as o:
                Mystem.write_plain(content_io, o)
            content_io.seek(0)
            with open(mystem_xml_path, 'wb') as o:
                Mystem.write_xml(content_io, o)
            content_io.seek(0)
            with open(src_plain_path, 'w') as f:
                f.write(
                    "@au %s\n@ti %s\n@da %s\n@topic %s\n@url %s\n%s"
                    % (
                        data['author'],
                        data['header'],
                        data['date'],
                        data['topic'],
                        data['source'],
                        content_io.read()
                    )
                )
        data.update({'path': src_plain_path})
        return data

    def update_metadata(self, data):
        if self._csv is not None:
            clean_data = {}
            for k in data.keys():
                if k in self.DATA_KEYS:
                    clean_data.update({k: data[k]})
            self._csv.write(clean_data)


class Mystem:

    @staticmethod
    def write_xml(src_file, out_file):
        cmd = [MYSTEM_BIN, "-e", Crawler.MAGAZINE_ENCODING, "--format", "xml"]
        out, err = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)\
            .communicate(bytes(src_file.read(), Crawler.MAGAZINE_ENCODING))
        out_file.write(out)

    @staticmethod
    def write_plain(src_file, out_file):
        cmd = [MYSTEM_BIN, "-e", Crawler.MAGAZINE_ENCODING, "--format", "text"]
        out, err = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE) \
            .communicate(bytes(src_file.read(), Crawler.MAGAZINE_ENCODING))
        out_file.write(out)


class CSV:

    _file = None
    _writer = None

    def __init__(self, path, keys):
        self._file = open(path, 'w')
        self._writer = csv.DictWriter(self._file, keys, delimiter='\t')
        self._writer.writeheader()

    def write(self, data):
        self._writer.writerow(data)