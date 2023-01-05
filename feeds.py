import feedparser
import unicodedata


def get_feed(RSS):
    feed = []
    nf = feedparser.parse(RSS)
    for entry in nf.entries:
        news = {}
        news['id'] = entry['id']
        news['title'] = unicodedata.normalize("NFKC", entry['title'])
        news['link'] = entry['link']
        news['description'] = unicodedata.normalize("NFKC", entry['description'])
        feed.append(news)
    return feed


def get_feed_lemonde():
    return get_feed("https://www.lemonde.fr/rss/une.xml")


def get_feed_figaro():
    return get_feed("https://www.lefigaro.fr/rss/figaro_actualites.xml")


def get_feed_liberation():
    return get_feed("https://www.liberation.fr/arc/outboundfeeds/rss/?outputType=xml")

print(get_feed_figaro())
