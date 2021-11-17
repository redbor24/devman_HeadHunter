import json
import requests

from config import SJ_SECRET_KEY


sj_headers = {
    'X-Api-App-Id': SJ_SECRET_KEY,
}

SUPERJOB_URL = 'https://api.superjob.ru/2.0/'


def get_entity_list(entity):
    resp = requests.get(url=SUPERJOB_URL + entity + '/')
    resp.raise_for_status()
    return resp.json()


def get_town(city):
    for town_n, town in enumerate(get_entity_list('town')['objects']):
        if town['title'] == city:
            return town['id'], city


def get_catalog(catalog):
    catalogues = []
    for entity_n, entity in enumerate(get_entity_list('catalogues')):
        if catalog.lower() in entity['title'].lower():
            catalogues.append(entity)
    return catalogues


if __name__ == '__main__':
    # entity_list = get_entity_list('catalogues')
    # # print(json.dumps(entity_list, indent=4, ensure_ascii=False))
    # for en_n, en in enumerate(entity_list):
    #     print(en['key'], ':', en['title'])
    # # cats = get_catalog('разраб')
    # # print(cats)
    # exit(0)

    sj_params = {
        'town': 'Москва',
        'catalogues': '33',
    }
    resp = requests.get(url=SUPERJOB_URL + 'vacancies/', headers=sj_headers,
                        params=sj_params)
    resp.raise_for_status()
    vacancies = resp.json()['objects']
    # print(json.dumps(vacancies, indent=4, ensure_ascii=False))
    for vac_n, vac in enumerate(vacancies):
        if 'программист' in vac['candidat'] \
                or 'программист' in vac['profession']:
            print(f"{vac['profession']}, {vac['town']['title']}")
