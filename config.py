import requests
import json
import pandas as pd
import telebot
from vedis import Vedis
from enum import Enum

per_page_filter = 50

hh_href = 'https://api.hh.ru/vacancies'

CSV_FILENAME = 'Vacancies.xlsx'
CSV_SHEETNAME = 'Sheet Vacancies'
CSV_HEADERS = ['Заголовок', 'Город', 'Зарплата', 'Адрес', 'Станция метро', 'Комания', 'Дата публикации', 'Ссылка',
               'Лого', 'Занятость']

token = '1906316193:AAGUum1mvgncDVA3EgL6npBWJIAu-4ybH5E'
db_file = "database.vdb"

class States(Enum):
    S_START = 0
    S_GET_TITLE = 1
    S_GET_CITY = 2
    S_PARSE_DONE = 3
