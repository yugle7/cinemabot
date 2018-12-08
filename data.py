import re


def normal(sentence):
    return re.sub(r'[^a-zа-я \d\n\t]', '', sentence.lower()).split()


def russian(sentence):
    return re.search(r'[а-я]', sentence)


class Film:
    def __init__(self, title, link, poster, number=0, rank=0):
        self.link = link
        self.title = title
        self.poster = poster
        self.number = number
        self.rank = rank

    def calc_rank(self, words):
        title = normal(self.title)
        self.rank = sum(word in words for word in title) - len(title) / 10
