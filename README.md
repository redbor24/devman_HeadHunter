# Учебный проект devman_HeadHunter
Получает с ресурсов HeadHunter.ru и SuperJob.ru статистику по вакансиям
по заданным языкам программирования и выводит в виде таблицы:
```
┌SuperJob. Москва───────┬──────────────────┬─────────────────────┬──────────────────┐
│ Язык программирования │ Вакансий найдено │ Вакансий обработано │ Средняя зарплата │
├───────────────────────┼──────────────────┼─────────────────────┼──────────────────┤
│ Python                │        96        │          65         │      87584       │
│ Java                  │        78        │          52         │      174153      │
│ JavaScript            │       144        │         189         │      89950       │
│ C++                   │        49        │          33         │      120833      │
│ C#                    │        45        │          28         │      108928      │
│ Delphi                │        12        │          10         │      85000       │
│ GO                    │        20        │          17         │      118676      │
│ PHP                   │        94        │          72         │      94406       │
│ Ruby                  │        9         │          8          │      150537      │
└───────────────────────┴──────────────────┴─────────────────────┴──────────────────┘
```
### Зависимости
```
requests==2.26.0
terminaltables==3.1.0
```
### Переменные окружения
 - `SJ_SECRET_KEY=<value>` - токен для работы с SuperJob.ru 
([получение токена](https://api.superjob.ru/register/))
### Список языков программирования для сбора статистики
Модуль `config.py` переменная `PROG_LANGS`
```
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
```
### Запуск скрипта
```
python pl_stat.py 
```