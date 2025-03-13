from box import Box
from datetime import datetime
from urllib import parse


def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    values = extract(obj, arr, key)
    return values


def get_articles(entries, tags):
    entires = Box(entries)
    tags = Box(tags)
    articles = []
    for item in entires.data:
        articles.append({
            "article_id":item.id, 
            "timestamp":datetime.timestamp(datetime.strptime(item.published, "%Y-%m-%dT%H:%M:%S.%fZ")), 
            "headline":item.title, 
            "summary":item.summary, 
            "url":item.url, 
            "source":parse.urlparse(item.url).netloc, 
            "tags": tags.data[item.feed_id] if item.feed_id in tags['data'].keys() else None
        })
    return articles
