import datetime
import json
import operator
import requests
from requests import exceptions

HH_BASE_URL = 'https://api.hh.ru/'
VAC_PER_PAGE = 20

HEADERS = {
    'content-type': 'application/json; charset=UTF-8',
}

hh_params = {
    'text': 'программист',
}

lang_details = {
    'vacancies_found': 0,
    'vacancies_processed': 0,
    'average_salary': 0,
}

proglangs = {
    # 'Python': 0,
    # 'Java': 0,
    # 'JavaScript': 0,
    # 'C++': 0,
    # 'C#': 0,
    # 'Delphi': 0,
    # 'GO': 0,
    'PHP': 0,
    'Ruby': 0,
}


def get_proglang_distribution():
    params = {}
    for lang_n, lang in enumerate(proglangs):
        params['text'] = 'программист ' + lang
        response = requests.get(HH_BASE_URL + r'vacancies/', headers=HEADERS, params=params)
        response.raise_for_status()
        _ = response.json()['found']
        proglangs[lang] = _ if _ > 100 else 0

    return {k: v for k, v in sorted(proglangs.items(),
                                    key=operator.itemgetter(1),
                                    reverse=True)}


def get_programmer_vacancies(headers, params):
    response = requests.get(
        HH_BASE_URL + r'vacancies/',
        headers=headers,
        params=params)
    response.raise_for_status()
    return response.json()


def get_vac_details(vacancy):
    vac_salary = vacancy['salary']
    return {'from': vac_salary['from'],
            'to': vac_salary['to'],
            'currency': vac_salary['currency'],
            'gross': vac_salary['gross'], }


def get_predict_rub_salary(vacancy):
    vac_sal = vacancy['salary']

    if vac_sal is None:
        return None

    if vac_sal['currency'] is None:
        return None

    if vac_sal['to'] is None:
        return vac_sal['from'] * 1.2

    if vac_sal['from'] is None:
        return vac_sal['to'] * 0.8

    return (vac_sal['from'] + vac_sal['to']) / 2


def print_lang_average_salaries(lang, vac_per_page):
    params = {'text': lang, 'per_page': vac_per_page}
    res = get_programmer_vacancies(HEADERS, params)
    for vac_n, vac in enumerate(res['items']):
        print(vac_n, get_predict_rub_salary(vac))


def get_proglang_stat(proglang, proglang_stat, vac_per_page):
    print(f'Подсчёт количества вакансий для "{proglang}"', end='')
    params = {
        'text': proglang,
        'per_page': vac_per_page,
        'page': '0',
    }
    salary_sum = 0
    vacs_processed = 0
    page = 0
    while True:
        try:
            resp = get_programmer_vacancies(HEADERS, params)
        except exceptions.HTTPError:
            break
        for vac_n, vac in enumerate(resp['items']):
            _ = get_predict_rub_salary(vac)
            if _ is not None:
                salary_sum += _
                vacs_processed += 1
        page += 1
        params['page'] = page
        print('.', end='')

    print('')
    proglang_stat_values = {
        'vacancies_found': resp["found"],
        'vacancies_processed': vacs_processed,
        'average_salary': int(salary_sum / vacs_processed)
    }
    proglang_stat[proglang] = proglang_stat_values
    return proglang_stat_values


if __name__ == '__main__':
    # print(f'Общий список вакансий "{hh_params["text"]}":')
    # print(json.dumps(get_programmer_vacancies(HEADERS, hh_params), indent=4, ensure_ascii=False))
    #
    # # Список вакансий "программист" для Москвы
    # hh_params['area'] = '1'
    # hh_response = get_programmer_vacancies(HEADERS, hh_params)
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
    #       f'{get_programmer_vacancies(HEADERS, hh_params)["found"]}')
    #
    # print(f'Вакансии по ЯП: {get_proglang_distribution()}')

    # ЗП по Питону
    # print_python_average_salaries(VAC_PER_PAGE)
    # print_lang_average_salaries('Python', 3)

    # Статистика по ЗП по ЯП
    # for lang_n, lang in enumerate(proglangs):
    #     print(get_proglang_stat(lang, 100))

    # stat = {}
    # stat = get_proglang_stat('Python', stat, 100)
    # print(stat)
    # exit(0)

    stat = {}
    for lang_n, lang in enumerate(proglangs):
        get_proglang_stat(lang, stat, 100)
    print(stat)
