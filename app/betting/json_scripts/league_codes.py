import requests
import os
from flask import Blueprint
from app.config import META_KEY


# retrieves the codes associated with each league and stores in json format

def get_league_codes():

    supported_leagues = [
        'FBP',
        'FBC',
        'BKP',
        'BKC',
        'BKD',
        'BBM',
        'HKN',
        'MMA',
        'PGA',
        'SOAUA',
        'SOASI',
        'SCAFC',
        'SOR',
        'SOG',
        'SCNA',
        'SCC',
        'SOC',
        'SOEFL',
        'SOE',
        'SOEFA',
        'SONCC',
        'SOINT',
        'SOS',
        'SOELC',
        'SOF',
        'SOM',
        'SOX',
        'SOMW',
        'OLYSM',
        'OLYSW',
        'SOSC',
        'SOI',
        'SCB',
        'SCU',
        'SOA',
        'SOAUW',
        'SOWW',
        'SOWW',
    ]

    parameters = {
        'apiKey': META_KEY
    }

    req = requests.get(
        f'https://scrimmage.api.areyouwatchingthis.com/api/sports.json?',
        params=parameters
    )

    data = req.json().get('results')

    sport_data = []

    for sport in data:
        d = []
        abv_data = sport.get('abbreviation')
        skip = False
        for s in sport['leagues']:
            s_data = {
                'name': s.get('name'),
                'code': s.get('code')
            }
            d.append(s_data)

        result = {abv_data: d}
        sport_data.append(result.copy())
    return {'data': sport_data}
