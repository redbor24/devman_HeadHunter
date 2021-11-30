from decouple import config


HH_BASE_URL = 'https://api.hh.ru/'
HH_HEADER = {
    'content-type': 'application/json; charset=UTF-8',
}

SJ_BASE_URL = 'https://api.superjob.ru/2.0/'
SJ_SECRET_KEY = config('SJ_SECRET_KEY', '')
SJ_HEADER = {
    'X-Api-App-Id': SJ_SECRET_KEY,
}

PROG_LANGS = [
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
