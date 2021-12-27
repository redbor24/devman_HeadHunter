import itertools
import logging

import requests
from decouple import config
from terminaltables import SingleTable

logger = logging.getLogger('pl_stat')


def salary_predict_hh(vacancy):
    vac_sal = vacancy['salary']

    if not vac_sal\
            or not vac_sal['currency']\
            or vac_sal['currency'] != 'RUR':
        return None

    return salary_predict(vac_sal['from'], vac_sal['to'])


def salary_predict_sj(vacancy):
    if not vacancy['currency'] or vacancy['currency'] != 'rub':
        return None

    return salary_predict(vacancy['payment_from'], vacancy['payment_to'])


def salary_predict(salary_from, salary_to):
    predicted_salary = 0
    if salary_to and salary_from:
        predicted_salary = (salary_from + salary_to) / 2
    elif not salary_to and salary_from:
        predicted_salary = salary_from * 1.2
    elif not salary_from and salary_to:
        predicted_salary = salary_to * 0.8
    return predicted_salary


def get_stat_by_proglang_sj(secret_key, language):
    header = {
        'X-Api-App-Id': secret_key,
    }
    catalog_index = 33
    vacs_per_page = 100
    params = {
        'town': 'Москва',
        'catalogues': catalog_index,
        'count': vacs_per_page,
        'keyword': language,
    }

    vacs_processed, salary_sum = 0, 0

    for page in itertools.count(start=0):
        params['page'] = page
        response = requests.get(
            url='https://api.superjob.ru/2.0/vacancies/',
            headers=header,
            params=params
        )
        response.raise_for_status()
        vacancies = response.json()

        for vac in vacancies['objects']:
            predicted_salary = salary_predict_sj(vac)
            if predicted_salary:
                salary_sum += predicted_salary
                vacs_processed += 1

        if not vacancies['more']:
            break

    vacs_found = vacancies['total']
    if vacs_processed:
        average_salary = int(salary_sum / vacs_processed)
    else:
        average_salary = salary_sum

    return {
        'vacancies_found': vacs_found,
        'vacancies_processed': vacs_processed,
        'average_salary': average_salary
    }


def get_stat_by_proglang_hh(language):
    header = {
        'content-type': 'application/json; charset=UTF-8',
    }
    params = {
        'per_page': 100,
        'text': language
    }

    vacs_processed, salary_sum = 0, 0

    for page in itertools.count(start=1):
        response = requests.get(
            url='https://api.hh.ru/vacancies/',
            headers=header,
            params=params)
        response.raise_for_status()
        vacancies = response.json()

        for vac in vacancies['items']:
            predicted_salary = salary_predict_hh(vac)
            if predicted_salary:
                salary_sum += predicted_salary
                vacs_processed += 1

        last_page = vacancies['pages']
        if page == last_page:
            break

        params['page'] = page

    vacs_found = vacancies['found']

    if vacs_processed:
        average_salary = int(salary_sum / vacs_processed)
    else:
        average_salary = salary_sum

    return {
        'vacancies_found': vacs_found,
        'vacancies_processed': vacs_processed,
        'average_salary': average_salary
    }


def get_sj_statistic(secret_key, languages):
    logger.info('Сбор статистики для SuperJob.ru')

    lang_stat = {}
    for language in languages:
        logger.info(f' Подсчёт количества вакансий для "{language}"...')
        lang_stat[language] = get_stat_by_proglang_sj(secret_key, language)

    return lang_stat


def get_hh_statistic(languages):
    logger.info('Сбор статистики для HeadHunter.ru')
    lang_stat = {}
    for language in languages:
        logger.info(f' Подсчёт количества вакансий для "{language}"...')
        lang_stat[language] = get_stat_by_proglang_hh(language)

    return lang_stat


def get_printable_table(stat, table_caption):
    column_aligns = {
        1: 'center',
        2: 'center',
        3: 'center',
    }

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
    table_instance.justify_columns.update(column_aligns)
    return table_instance.table


def main():
    prog_langs = [
        'Parseltang',
        'Fortran',
        'Delphi',
        # 'Python',
        # 'Java',
        # 'JavaScript',
        # 'C++',
        # 'C',
        # 'GO',
        # 'PHP',
        # 'Ruby',
    ]

    sj_secret_key = config('SJ_SECRET_KEY', '')

    logger.setLevel(logging.INFO)
    log_handler = logging.FileHandler('pl_stat.log', encoding='utf-8')
    log_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(message)s')
    )
    logger.addHandler(log_handler)

    hh_stat = get_hh_statistic(prog_langs)
    printable_table = get_printable_table(hh_stat, 'HeadHunter. Москва')
    print(printable_table)
    logger.info(f'Результат:\n{printable_table}')

    sj_stat = get_sj_statistic(sj_secret_key, prog_langs)
    printable_table = get_printable_table(sj_stat, 'SuperJob. Москва')
    print(printable_table)
    logger.info(f'Результат:\n{printable_table}')


if __name__ == '__main__':
    main()
