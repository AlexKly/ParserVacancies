import requests
import json
import pandas as pd
import telebot
from vedis import Vedis
from enum import Enum
from tqdm import tqdm
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats

per_page_filter = 50

MIN_VALUE = 0
MAX_VALUE = 1e6
STEP_VALUE = 5000

hh_href = 'https://api.hh.ru/vacancies'
currency_href = 'https://www.cbr-xml-daily.ru/daily_json.js'

CSV_FILENAME = 'Vacancies_'
CSV_FORMAT = '.xlsx'
CSV_SHEETNAME = 'Sheet Vacancies'
CSV_HEADERS = ['Заголовок', 'Город', 'Зарплата', 'Адрес', 'Станция метро', 'Комания', 'Дата публикации', 'Ссылка',
               'Лого', 'Занятость']

DISTRIBUTION_FILENAME = 'dist_salary_'
DISTRIBUTION_FORMAT = '.png'

token = '1906316193:AAGUum1mvgncDVA3EgL6npBWJIAu-4ybH5E'
db_file = "database.vdb"


class States(Enum):
    S_START = "0"
    S_GET_TITLE = "1"
    S_GET_CITY = "2"
