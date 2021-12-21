import itertools
import logging
import math

import requests
from decouple import config
from terminaltables import SingleTable


def predict_salary_hh(vacancy):
    vac_sal = vacancy['salary']

    if not vac_sal or not vac_sal['currency']:
        return None

    return predict_salary(vac_sal['from'], vac_sal['to'])


def predict_salary_sj(vacancy):
    if not vacancy['currency']:
        return None

    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def predict_salary(salary_from, salary_to):
    if not salary_to and salary_from:
        sal_from = salary_from * 1.2
    else:
        sal_from = 0

    if not salary_from and salary_to:
        sal_to = salary_to * 0.8
    else:
        sal_to = 0

    predicted_salary = (sal_from + sal_to) / 2
    if predicted_salary:
        return predicted_salary
    else:
        return None


def get_proglang_stat_sj(languages):
    sj_header = {
        'X-Api-App-Id': SJ_SECRET_KEY,
    }
    sj_catalog_index = 33
    sj_vacs_per_page = 100
    params = {
        'town': 'Москва',
        'catalogues': sj_catalog_index,
        'count': sj_vacs_per_page,
    }

    logger.info('Сбор статистики для SuperJob.ru')
    lang_stat = {}
    for language in languages:
        logger.info(f' Подсчёт количества вакансий для "{language}"...')
        vacs_found, vacs_processed, salary_sum = 0, 0, 0

        params['keyword'] = language
        for page in itertools.count(start=0):
            params['page'] = page
            response = requests.get(
                url='https://api.superjob.ru/2.0/vacancies/',
                headers=sj_header,
                params=params
            )
            response.raise_for_status()
            vacancies = response.json()

            if page == 0:
                vacs_found = vacancies['total']

            for vac in vacancies['objects']:
                if vac['currency'] == 'rub':
                    predicted_salary = predict_salary_sj(vac)
                    if predicted_salary:
                        salary_sum += predicted_salary
                        vacs_processed += 1

            if not vacancies['more']:
                break

        average_salary = int(
            salary_sum / 1 if not vacs_processed else vacs_processed
        )
        lang_stat[language] = {
            'vacancies_found': vacs_found,
            'vacancies_processed': vacs_processed,
            'average_salary': average_salary
        }
    return lang_stat


def get_proglang_stat_hh(languages):
    hh_header = {
        'content-type': 'application/json; charset=UTF-8',
    }
    params = {
        'per_page': 100,
    }

    logger.info('Сбор статистики для HeadHunter.ru')
    lang_stat = {}
    for language in languages:
        params['text'] = language

        logger.info(f' Подсчёт количества вакансий для "{language}"...')

        last_page = 0
        vacs_found, vacs_processed, salary_sum = 0, 0, 0

        for page in itertools.count(start=1):
            response = requests.get(
                url='https://api.hh.ru/vacancies/',
                headers=hh_header,
                params=params)
            response.raise_for_status()
            vacancies = response.json()

            for vac in vacancies['items']:
                if vac['salary'] and vac['salary']['currency'] == 'RUR':
                    predicted_salary = predict_salary_hh(vac)
                    if predicted_salary:
                        salary_sum += predicted_salary
                        vacs_processed += 1

            if page == 1:
                last_page = vacancies['pages']
                vacs_found = vacancies['found']

            if page == last_page:
                break
            params['page'] = page

        average_salary = int(
            salary_sum / 1 if not vacs_processed else vacs_processed
        )
        lang_stat[language] = {
            'vacancies_found': vacs_found,
            'vacancies_processed': vacs_processed,
            'average_salary': average_salary
        }
    return lang_stat


def get_printable_table(stat, table_caption, column_aligns):
    terminal_table = [[
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]]

    for lang, lang_details in stat.items():
        terminal_table.append([
            lang,
            lang_details['vacancies_found'],
            lang_details['vacancies_processed'],
            lang_details['average_salary']]
        )

    table_instance = SingleTable(terminal_table, table_caption)
    for item_n, item in enumerate(column_aligns.items()):
        table_instance.justify_columns[item_n] = item
    logger.info(f'Результат:\n{table_instance.table}')
    return table_instance.table


if __name__ == '__main__':
    SJ_SECRET_KEY = config('SJ_SECRET_KEY', '')

    col_aligns = {
        1: 'center',
        2: 'center',
        3: 'center',
    }

    prog_langs = [
        'Fortran',
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

    logger = logging.getLogger('pl_stat')
    logger.setLevel(logging.DEBUG)
    log_handler = logging.FileHandler('pl_stat.log', encoding='utf-8')
    log_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(message)s')
    )
    logger.addHandler(log_handler)

    # hh_stat = get_proglang_stat_hh(prog_langs)
    # print(get_printable_table(hh_stat, 'HeadHunter. Москва', col_aligns))

    sj_stat = get_proglang_stat_sj(prog_langs)
    print(get_printable_table(sj_stat, 'SuperJob. Москва', col_aligns))
