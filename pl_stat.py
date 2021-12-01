import math

import requests
from requests import exceptions
from terminaltables import SingleTable

from config import (
    HH_BASE_URL,
    HH_HEADER,
    SJ_BASE_URL,
    SJ_HEADER,
)

resources = ['HeadHunter.ru', 'SuperJob.ru']

col_aligns = {
    1: 'center',
    2: 'center',
    3: 'center',
}

lang_details = {
    'vacancies_found': 0,
    'vacancies_processed': 0,
    'average_salary': 0,
}


def predict_salary_hh(vacancy):
    vac_sal = vacancy['salary']

    if vac_sal is None:
        return None

    if vac_sal['currency'] is None:
        return None

    return predict_salary(vac_sal['from'], vac_sal['to'])


def predict_salary_sj(vacancy):
    if vacancy['currency'] is None:
        return None

    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_salary(salary_from, salary_to):
    # if salary_to is None or salary_to == 0:
    if salary_to is None:
        return None if salary_from * 1.2 == 0 else salary_from * 1.2

    # if salary_from is None or salary_from == 0:
    if salary_from is None:
        return None if salary_to * 0.8 == 0 else salary_to * 0.8

    predicted_salary = (salary_from + salary_to) / 2
    return None if predicted_salary == 0 else predicted_salary


def get_proglang_stat_hh(proglang, proglang_stat):
    print(f'Подсчёт количества вакансий для "{proglang}"...')
    params = {
        'text': proglang,
        'per_page': 100,
        'page': '0',
    }
    vac_total, vacs_processed, salary_sum, average_salary, page = 0, 0, 0, 0, 0
    if proglang in proglang_stat:
        proglang_stat_values = proglang_stat[proglang]
        vac_total += proglang_stat_values['vacancies_found']
        vacs_processed += proglang_stat_values['vacancies_processed']
        average_salary += proglang_stat_values['average_salary']
        salary_sum = average_salary * vacs_processed

    while True:
        try:
            response = requests.get(
                HH_BASE_URL + r'vacancies/',
                headers=HH_HEADER,
                params=params)
            response.raise_for_status()
            vacancies = response.json()
        except exceptions.HTTPError:
            break

        for vac_n, vac in enumerate(vacancies['items']):
            if vac['salary']:
                if vac['salary']['currency'] == 'RUR':
                    predicted_salary = predict_salary_hh(vac)
                    if predicted_salary:
                        salary_sum += predicted_salary
                        vacs_processed += 1
        page += 1
        params['page'] = page

    proglang_stat_values = {
        'vacancies_found': vacancies['found'],
        'vacancies_processed': vacs_processed,
        'average_salary': int(salary_sum / vacs_processed)
    }
    proglang_stat[proglang] = proglang_stat_values

    return proglang_stat


def get_proglang_stat_sj(proglang, proglang_stat):
    print(f'Подсчёт количества вакансий для "{proglang}"...')
    params = {
        'town': 'Москва',
        'catalogues': '33',
        'keyword': proglang,
        'page': '0',
        'count': 100
    }
    response = requests.get(
        url=SJ_BASE_URL + 'vacancies/',
        headers=SJ_HEADER,
        params=params
    )
    response.raise_for_status()
    vac_total = response.json()['total']
    vac_on_page = 20
    pages = math.ceil(vac_total / vac_on_page)
    vacs_processed, salary_sum, average_salary, page = 0, 0, 0, 0
    if proglang in proglang_stat:
        proglang_stat_values = proglang_stat[proglang]
        vac_total += proglang_stat_values['vacancies_found']
        vacs_processed += proglang_stat_values['vacancies_processed']
        average_salary += proglang_stat_values['average_salary']
        salary_sum = average_salary * vacs_processed

    while page < pages:
        resp = requests.get(
            url=SJ_BASE_URL + 'vacancies/',
            headers=SJ_HEADER,
            params=params
        )
        resp.raise_for_status()
        page += 1
        vacancies = resp.json()
        for vac_n, vac in enumerate(vacancies['objects']):
            if vac['currency'] == 'rub':
                predicted_salary = predict_salary_sj(vac)
                if predicted_salary:
                    salary_sum += predicted_salary
                    vacs_processed += 1
        params['page'] = page

    proglang_stat_values = {
        'vacancies_found': vac_total,
        'vacancies_processed': vacs_processed,
        'average_salary': int(salary_sum / vacs_processed)
    }
    proglang_stat[proglang] = proglang_stat_values
    return proglang_stat


def get_stat(resource, languages):
    if resource not in resources:
        raise KeyError(resource)

    langs = {}
    for lang_n, lang in enumerate(languages):
        langs[lang] = 0

    stat = {}
    print(resource)
    for lang_n, lang in enumerate(langs):
        if resource == 'HeadHunter.ru':
            stat = get_proglang_stat_hh(lang, stat)
        if resource == 'SuperJob.ru':
            stat = get_proglang_stat_sj(lang, stat)
    return stat


def convert_data_for_tables(data_array):
    result = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]
    for el in data_array.items():
        result.append([
            el[0],
            el[1]['vacancies_found'],
            el[1]['vacancies_processed'],
            el[1]['average_salary']]
        )
    return result


def print_table(stat, table_caption, column_aligns):
    if not stat:
        return
    table_instance = SingleTable(convert_data_for_tables(stat), table_caption)
    for item in column_aligns.items():
        table_instance.justify_columns[item[0]] = item[1]
    print(table_instance.table)
    print()


if __name__ == '__main__':
    prog_langs = [
        'Python',
        'Java',
        'JavaScript',
        'C++',
        'C',
        'Delphi',
        'GO',
        'PHP',
        'Ruby',
    ]

    try:
        hh_stat = get_stat('HeadHunter.ru', prog_langs)
        sj_stat = get_stat('SuperJob.ru', prog_langs)

        print_table(hh_stat, 'HeadHunter. Москва', col_aligns)
        print_table(sj_stat, 'SuperJob. Москва', col_aligns)
    except KeyError as e:
        print(f'Ошибка! Ресурс {e} не найден')
