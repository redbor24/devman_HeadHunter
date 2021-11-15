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

    # Список вакансий "программист" для Москвы
    params['area'] = '1'
    hh_response = programmer_vacancies()
    print(json.dumps(hh_response, indent=4, ensure_ascii=False))

    # Общее количество вакансий
    print(f'Общее количество вакансий "{params["text"]}" для Москвы: '
          f'{hh_response["found"]}')

    # Список вакансий "программист" для Москвы за последний месяц
    today = datetime.datetime.today()
    params['date_from'] = (today + datetime.timedelta(days=-30)).\
        strftime('%Y-%m-%d')
    params['date_to'] = today.strftime('%Y-%m-%d')
    print(f'Количество вакансий "{params["text"]}'
          f'" для Москвы за последний месяц: '
          f'{programmer_vacancies()["found"]}')
