import datetime
import json
import operator
import requests

HH_BASE_URL = 'https://api.hh.ru/'

HEADERS = {
    'content-type': 'application/json; charset=UTF-8',
}

hh_params = {
    'text': 'программист',
}

lang_list = {
    'Python': 0,
    'Java': 0,
    'JavaScript': 0,
    'C++': 0,
    'C#': 0,
    'Delphi': 0,
    'GO': 0,
    'PHP': 0,
    'Ruby': 0,
}


def get_proglang_distribution():
    params = {}
    for lang_n, lang in enumerate(lang_list):
        params['text'] = 'программист ' + lang
        response = requests.get(HH_BASE_URL + r'vacancies/', headers=HEADERS, params=params)
        response.raise_for_status()
        _ = response.json()['found']
        lang_list[lang] = _ if _ > 100 else 0

    return {k: v for k, v in sorted(lang_list.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)}


def programmer_vacancies(params):
    response = requests.get(
        HH_BASE_URL + r'vacancies/',
        headers=HEADERS,
        params=params)
    response.raise_for_status()
    return response.json()


def get_vac_details(vacancy):
    vac_salary = vacancy['salary']
    return {'from': vac_salary['from'],
            'to': vac_salary['to'],
            'currency': vac_salary['currency'],
            'gross': vac_salary['gross'], }


def predict_rub_salary(vacancy):
    vac_sal = vacancy['salary']

    if vac_sal['currency'] is None:
        return None

    if vac_sal['to'] is None:
        return vac_sal['from'] * 1.2

    if vac_sal['from'] is None:
        return vac_sal['to'] * 0.8

    return (vac_sal['from'] + vac_sal['to']) / 2


if __name__ == '__main__':
    # print(f'Общий список вакансий "{hh_params["text"]}":')
    # print(json.dumps(programmer_vacancies(hh_params), indent=4, ensure_ascii=False))
    #
    # # Список вакансий "программист" для Москвы
    # hh_params['area'] = '1'
    # hh_response = programmer_vacancies(hh_params)
    # print(json.dumps(hh_response, indent=4, ensure_ascii=False))
    #
    # # Общее количество вакансий
    # print(f'Общее количество вакансий "{hh_params["text"]}" для Москвы: '
    #       f'{hh_response["found"]}')
    #
    # # Список вакансий "программист" для Москвы за последний месяц
    # today = datetime.datetime.today()
    # hh_params['date_from'] = (today + datetime.timedelta(days=-30)).\
    #     strftime('%Y-%m-%d')
    # hh_params['date_to'] = today.strftime('%Y-%m-%d')
    # print(f'Количество вакансий "{hh_params["text"]}'
    #       f'" для Москвы за последний месяц: '
    #       f'{programmer_vacancies(hh_params)["found"]}')
    #
    # print(f'Вакансии по ЯП: {get_proglang_distribution()}')

    # ЗП по Питону
    hh_params['per_page'] = 20
    hh_params['text'] = 'Python'
    res = programmer_vacancies(hh_params)
    for vac_n, vac in enumerate(res['items']):
        try:
            print(vac_n, predict_rub_salary(vac))
        except TypeError:
            print(vac_n, None)
