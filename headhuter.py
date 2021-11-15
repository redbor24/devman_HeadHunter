import json
import requests


HH_BASE_URL = 'https://api.hh.ru/'

HEADERS = {
    'content-type': 'application/json; charset=UTF-8',
}

params = {
    'text': 'программист',
}


def programmer_vacancies():
    response = requests.get(
            HH_BASE_URL + r'vacancies/',
            headers=HEADERS,
            params=params)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))


if __name__ == '__main__':
    programmer_vacancies()
