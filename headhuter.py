import datetime
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
    return response.json()


if __name__ == '__main__':
    print(f'Общий список вакансий "{params["text"]}":')
    print(json.dumps(programmer_vacancies(), indent=4, ensure_ascii=False))
