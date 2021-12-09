import logging
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


def predict_salary_hh(vacancy):
    vac_sal = vacancy['salary']

    if not vac_sal:
        return None

    if not vac_sal['currency']:
        return None

    return predict_salary(vac_sal['from'], vac_sal['to'])


def predict_salary_sj(vacancy):
    if not vacancy['currency']:
        return None

    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_salary(salary_from, salary_to):
    if not salary_to:
        return salary_from * 1.2 if salary_from * 1.2 else None

    if not salary_from:
        return salary_to * 0.8 if salary_to * 0.8 else None

    predicted_salary = (salary_from + salary_to) / 2
    return predicted_salary if predicted_salary else None


def get_proglang_stat_sj(proglang):
    logger.info(f'Подсчёт количества вакансий для "{proglang}"...')
    sj_ITcatalog_index = 33
    params = {
        'town': 'Москва',
        'catalogues': sj_ITcatalog_index,
        'keyword': proglang,
    }
    page, pages, vac_on_page = 0, 1, 100
    vacs_processed, salary_sum = 0, 0

    while page < pages:
        response = requests.get(
            url=f'{SJ_BASE_URL}vacancies/',
            headers=SJ_HEADER,
            params=params
        )
        response.raise_for_status()
        vacancies = response.json()
        if page == 0:
            vac_total = vacancies['total']
            pages = math.ceil(vac_total / vac_on_page)

        for vac in vacancies['objects']:
            if vac['currency'] == 'rub':
                predicted_salary = predict_salary_sj(vac)
                if predicted_salary:
                    salary_sum += predicted_salary
                    vacs_processed += 1
        page += 1
        params['page'] = page

    vacs_processed = 1 if not vacs_processed else vacs_processed
    return {
        'vacancies_found': vac_total,
        'vacancies_processed': vacs_processed,
        'average_salary': int(salary_sum / vacs_processed)
    }


def get_proglang_stat_hh(proglang):
    logger.info(f'Подсчёт количества вакансий для "{proglang}"...')
    params = {
        'text': proglang,
        'per_page': 100,
        'page': '0',
    }
    vacs_processed, salary_sum, page = 0, 0, 0

    while True:
        try:
            response = requests.get(
                f'{HH_BASE_URL}vacancies/',
                headers=HH_HEADER,
                params=params)
            response.raise_for_status()
            vacancies = response.json()
        except exceptions.HTTPError:
            break

        for vac in vacancies['items']:
            if vac['salary'] and vac['salary']['currency'] == 'RUR':
                predicted_salary = predict_salary_hh(vac)
                if predicted_salary:
                    salary_sum += predicted_salary
                    vacs_processed += 1
        page += 1
        params['page'] = page

    vacs_processed = 1 if not vacs_processed else vacs_processed
    return {
        'vacancies_found': vacancies['found'],
        'vacancies_processed': vacs_processed,
        'average_salary': int(salary_sum / vacs_processed)
    }


def get_stat(resource, languages):
    logger.info(f'Сбор статистики для {resource}.')
    if resource not in resources:
        raise KeyError(resource)

    lang_stat = {}
    langs = {lang: 0 for lang in languages}
    for lang_n, lang in enumerate(langs):
        if resource == 'HeadHunter.ru':
            lang_stat[lang] = get_proglang_stat_hh(lang)
        if resource == 'SuperJob.ru':
            lang_stat[lang] = get_proglang_stat_sj(lang)
    return lang_stat


def prepare_terminal_table(data_array):
    result = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]

    for lang, lang_details in data_array.items():
        result.append([
            lang,
            lang_details['vacancies_found'],
            lang_details['vacancies_processed'],
            lang_details['average_salary']]
        )

    return result


def print_table(stat, table_caption, column_aligns):
    if not stat:
        return
    table_instance = SingleTable(prepare_terminal_table(stat), table_caption)
    for item in column_aligns.items():
        table_instance.justify_columns[item[0]] = item[1]
    print(table_instance.table)
    print()


if __name__ == '__main__':
    prog_langs = [
        'Python',
        'Java',
        # 'JavaScript',
        # 'C++',
        # 'C',
        # 'Delphi',
        # 'GO',
        # 'PHP',
        # 'Ruby',
    ]

    logger = logging.getLogger('pl_stat')
    logger.setLevel(logging.INFO)
    log_handler = logging.FileHandler('pl_stat.log')
    log_foramatter = logging.Formatter('%(asctime)s - %(message)s')
    log_handler.setFormatter(log_foramatter)
    logger.addHandler(log_handler)

    try:
        # hh_stat = get_stat('HeadHunter.ru', prog_langs)
        # print_table(hh_stat, 'HeadHunter. Москва', col_aligns)

        sj_stat = get_stat('SuperJob.ru', prog_langs)
        print_table(sj_stat, 'SuperJob. Москва', col_aligns)
    except KeyError as e:
        print(f'Ошибка! Ресурс {e} не найден')
