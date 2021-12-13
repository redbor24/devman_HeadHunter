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
    SJ_HEADER = {
        'X-Api-App-Id': SJ_SECRET_KEY,
    }

    logger.info('Сбор статистики для SuperJob.ru')
    lang_stat = {}
    sj_catalog_index = 33
    for lang_n, language in enumerate(languages):
        logger.info(f' Подсчёт количества вакансий для "{language}"...')
        params = {
            'town': 'Москва',
            'catalogues': sj_catalog_index,
            'keyword': language,
        }
        vac_on_page, vacs_processed, salary_sum = 100, 0, 0

        response = requests.get(
            url='https://api.superjob.ru/2.0/vacancies/',
            headers=SJ_HEADER,
            params=params
        )
        response.raise_for_status()
        vacancies = response.json()

        vac_total = vacancies['total']
        pages = math.ceil(vac_total / vac_on_page)

        for page in itertools.count(start=1):
            for vac in vacancies['objects']:
                if vac['currency'] == 'rub':
                    predicted_salary = predict_salary_sj(vac)
                    if predicted_salary:
                        salary_sum += predicted_salary
                        vacs_processed += 1

            params['page'] = page
            response = requests.get(
                url=f'{SJ_BASE_URL}vacancies/',
                headers=SJ_HEADER,
                params=params
            )
            response.raise_for_status()
            vacancies = response.json()

            if page == pages:
                break

        vacs_processed = 1 if not vacs_processed else vacs_processed
        lang_stat[language] = {
            'vacancies_found': vac_total,
            'vacancies_processed': vacs_processed,
            'average_salary': int(salary_sum / vacs_processed)
        }
    return lang_stat


def get_proglang_stat_hh(languages):
    HH_HEADER = {
        'content-type': 'application/json; charset=UTF-8',
    }

    logger.info('Сбор статистики для HeadHunter.ru')
    lang_stat = {}
    for lang_n, language in enumerate(languages):
        logger.info(f' Подсчёт количества вакансий для "{language}"...')
        params = {
            'text': language,
            'per_page': 100,
            'page': '0',
        }

        response = requests.get(
            'https://api.hh.ru/vacancies/',
            headers=HH_HEADER,
            params=params)
        response.raise_for_status()
        vacancies = response.json()
        pages = vacancies['pages']
        last_page = pages - 1
        vacs_processed, salary_sum = 0, 0

        for page in itertools.count(start=1):
            for vac in vacancies['items']:
                if vac['salary'] and vac['salary']['currency'] == 'RUR':
                    predicted_salary = predict_salary_hh(vac)
                    if predicted_salary:
                        salary_sum += predicted_salary
                        vacs_processed += 1
            params['page'] = page

            response = requests.get(
                f'{HH_BASE_URL}vacancies/',
                headers=HH_HEADER,
                params=params)
            response.raise_for_status()
            vacancies = response.json()

            if page == last_page:
                break

        vacs_processed = 1 if not vacs_processed else vacs_processed
        lang_stat[language] = {
            'vacancies_found': vacancies['found'],
            'vacancies_processed': vacs_processed,
            'average_salary': int(salary_sum / vacs_processed)
        }
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
    logger.info(f'\n{table_instance.table}')
    print(table_instance.table)
    print()


if __name__ == '__main__':
    SJ_SECRET_KEY = config('SJ_SECRET_KEY', '')

    col_aligns = {
        1: 'center',
        2: 'center',
        3: 'center',
    }

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

    logger = logging.getLogger('pl_stat')
    logger.setLevel(logging.DEBUG)
    log_handler = logging.FileHandler('pl_stat.log', encoding='utf-8')
    log_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(message)s')
    )
    logger.addHandler(log_handler)

    hh_stat = get_proglang_stat_hh(prog_langs)
    print_table(hh_stat, 'HeadHunter. Москва', col_aligns)

    sj_stat = get_proglang_stat_sj(prog_langs)
    print_table(sj_stat, 'SuperJob. Москва', col_aligns)
