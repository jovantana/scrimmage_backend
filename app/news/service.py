import requests
import json

from werkzeug.wrappers import response
from app import Config

session = requests.Session()
session.auth = (Config.FEEDS_USEAREMAIL, Config.FEEDS_PASSWORD)


def get_entries(params):
    """
    get entries from feedbin filterd by params
    """
    url = Config.FEEDS_BASEURL+"entries.json"
    response = session.get(url, params=params)
    if response.ok:
        return {"data":response.json(), "status_code":response.status_code}
    return {"status_code":response.status_code, "reason":response.reason}


def get_unread_entries():
    url =  Config.FEEDS_BASEURL+'unread_entries.json'
    response = session.get(url)
    if response.ok:
        return response
    return {"status_code":response.status_code, "reason":response.reason}


def update_read_status(ids, read=True):
    url = Config.FEEDS_BASEURL+'unread_entries.json'
    data = {'unread_entries':ids}
    if read:
        # will mark the specified entry_ids as read.
        response = session.delete(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
            
        if response.ok:
            print('ids has been successfully marked as read')
        else:
            print(response.status_code)
            raise ValueError('not able to update the articles status!')
    else:
        # will mark the specified entry_ids as unread.
        response = session.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
    return response.status_code


def get_tags():
    """
    to get feeds tags from feedbin
    """
    url = Config.FEEDS_BASEURL+'taggings.json'
    response = session.get(url)
    if response.ok:
        feed_tags = dict()
        for item in response.json():
            feed_tags.setdefault(item['feed_id'], []).append(item['name'])
        return {"data":feed_tags, "status_code":response.status_code}
    return {"status_code":response.status_code, "reason":response.reason}
