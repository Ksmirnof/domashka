from MagazineWalker import *

crw = Crawler(False)
data = crw.get_data("http://unecha-gazeta.ru/aktualno/2328-VUNECHEOTKRITTSENTRTEHNICHESKOGOOBRAZOVANIYA.html")

print(
    "Название: %s\nИмя автора: %s\nДата публикации: %s\nКатегории: %s\n"
    % (data['header'], data['author'], data['date'], data['topic'])
)
