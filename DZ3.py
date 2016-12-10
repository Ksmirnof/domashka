import urllib.request, re, html

def links():
    f = open('links.txt', 'r', encoding = 'UTF-8')
    link = []
    for m in f:
        link.append(m)
    f.close()
    return link

def reg(link):
    for link in links:
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        req = urllib.request.Request(link, headers={'User-Agent':user_agent})
        with urllib.request.urlopen(req) as response:
            html_page = response.read().decode('utf-8')
            for reg in regs:
                regLink = re.compile(reg, flags=re.U | re.DOTALL)
                text = regLink.search(html_page)
                texts.append(new_text)
    return texts

def wordsets(texts):
    sets = []
    for elem in tex:
        sets.append(set(elem))
    return sets

def words(texts):
    d = []
    for elements in texts:
        for element in elements:
            if element in d:
                d[element] += 1
            else:
                d[element] = 1
                print(d)
    return d

def intersection(sets):

def main():

if __name__ == '__main__':
    main()
