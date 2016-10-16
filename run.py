from MagazineWalker import *


def run(max_links_count):
    crw = Crawler()
    links = crw.get_links(max_links_count)
    for l in links:
        data = crw.get_data(l)
        data = crw.create_files(data)
        crw.update_metadata(data)

run(200)
