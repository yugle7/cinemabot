import json
import requests
import logging
from heapq import nlargest

from data import normal, Film, russian

logging.basicConfig(
    format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
    level=logging.INFO)


class IMDb:
    api = 'http://sg.media-imdb.com/suggests/'
    url = 'https://www.imdb.com/title/'

    def get_by_title(self, title):
        logging.debug(f'get film by its title: {title}')
        req = requests.get(f'{self.api}{title[0]}/{title}.json')

        if not req.ok:
            logging.warning(f'bad request from {self.url}')
            return []

        res = req.text[len('imdb$') + len(title) + 1:-1]
        res = json.loads(res)

        return self.filter_films(res['d']) if 'd' in res else []

    def get_by_number(self, number):
        number = 'tt' + str(number).zfill(7)

        logging.debug(f'get film by its number: {number}')
        req = requests.get(f'{self.api}t/{number}.json')

        if not req.ok:
            logging.warning(f'bad request from {self.url}')
            return None

        res = req.text[len('imdb$') + len(number) + 1:-1]
        res = json.loads(res)

        if 'd' not in res or not res['d']:
            return None

        return self.info_to_film(res['d'][0])

    def info_to_film(self, info):
        link = f'{self.url}{info["id"]}/'
        title = info['l']
        poster = ''

        if 'i' not in info:
            logging.info(f'film {title} without poster')
        else:
            poster = info['i'][0]

        return Film(title, link, poster)

    def filter_films(self, films):
        logging.debug(f'filter {len(films)} results')

        for info in films:
            if 'q' not in info:
                continue
            if 'i' not in info:
                continue
            if 'l' not in info:
                continue

            if info['q'] not in ['feature', 'TV series']:
                continue

            yield self.info_to_film(info)


class RUDb:
    def __init__(self):
        self.fw = {}
        self.wf = {}

        fw = open('data/fw.csv', mode='r', encoding='utf-8')
        for q in fw:
            film, words = q[:-1].split('\t')
            self.fw[int(film)] = words
        fw.close()

        wf = open('data/wf.csv', mode='r', encoding='utf-8')
        for q in wf:
            word, films = q[:-1].split('\t')
            self.wf[word] = films
        wf.close()

    def get_by_words(self, words):
        films = set()
        for word in words:
            if word in self.wf:
                films.update(map(int, self.wf[word].split()))

        for film in films:
            title = self.fw[film]
            yield Film(title, '', '', film)


imdb = IMDb()
rudb = RUDb()


def search(query):
    words = normal(query)
    title = ' '.join(words)

    if not title:
        logging.info(f'title is empty')
        return

    films = []
    if not russian(title):
        films = list(imdb.get_by_title(title))

    if films:
        for film in films:
            film.calc_rank(words)
        for film in nlargest(3, films, key=lambda q: q.rank):
            if film.rank > 0:
                yield film
    else:
        logging.info(f'lets search in local data base: {title}')

        films = list(rudb.get_by_words(words))
        for film in films:
            film.calc_rank(words)

        for film in nlargest(3, films, key=lambda q: q.rank):
            movie = imdb.get_by_number(film.number)
            if movie:
                movie.title += ' (' + film.title + ')'
                yield movie
            else:
                logging.warning(f'there is no such number: {film.number}')
