import feedparser
import unicodedata


def get_feed_lemonde():
    titles = []
    RSS = "https://www.lemonde.fr/rss/une.xml"
    nf = feedparser.parse(RSS)
    for entry in nf.entries:
        title = unicodedata.normalize("NFKC", entry['title'])
        titles.append(title)
    return titles

print(get_feed_lemonde())