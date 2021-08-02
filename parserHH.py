import config


def getPage(page=0, title='', area=113):
    params = {
        'text': title,
        'area': area,
        'page': page,
        'per_page': config.per_page_filter
    }

    req = config.requests.get(config.hh_href, params)
    data = req.content.decode()
    req.close()

    return data


def formedSalary(salary_type):
    if salary_type is None:
        str_salary = 'Цена Н/У'
    else:
        salary_from = salary_type['from']
        salary_to = salary_type['to']
        salary_currency = salary_type['currency']
        if salary_from is not None and salary_to is not None:
            str_salary = str(salary_from) + '-' + str(salary_to) + ' ' + str(salary_currency)
        elif salary_from is not None and salary_to is None:
            str_salary = 'От ' + str(salary_from) + ' ' + str(salary_currency)
        elif salary_from is None and salary_to is not None:
            str_salary = 'До ' + str(salary_to) + ' ' + str(salary_currency)
        else:
            str_salary = 'Цена Н/У'

    return str_salary


def dist_salary(salary_type, USD_VALUE, EUR_VALUE):
    if salary_type is None:
        value = None
    else:
        coef_currency = 1
        value = list()
        if salary_type['currency'] == 'RUR':
            coef_currency = 1
        elif salary_type['currency'] == 'USD':
            coef_currency = USD_VALUE['Value']
        elif salary_type == 'EUR':
            coef_currency = EUR_VALUE['Value']

        if salary_type['from'] is not None and salary_type['to'] is not None:
            value.append(salary_type['from'] * coef_currency)
            value.append(salary_type['to'] * coef_currency)
        elif salary_type['from'] is not None and salary_type['to'] is None:
            value.append(salary_type['from'] * coef_currency)
        elif salary_type['from'] is None and salary_type['to'] is not None:
            value.append(salary_type['to'] * coef_currency)
        else:
            value = None

        return value


def form_dist_salary(list_dist_salary, step_salary, user_id):
    new_mas = config.np.zeros(1)
    for i in range(len(list_dist_salary)):
        if list_dist_salary[i] is not None:
            if len(list_dist_salary[i]) > 1:
                range_values = config.np.arange(list_dist_salary[i][0], list_dist_salary[i][1], step_salary)
            else:
                range_values = list_dist_salary[i]
            new_mas = config.np.concatenate((new_mas, range_values), axis=0)
    new_mas = config.np.delete(new_mas, 0, axis=0)

    list_value_stat = list()
    min_data = config.np.min(new_mas, axis=0)
    list_value_stat.append(min_data)
    max_data = config.np.max(new_mas, axis=0)
    list_value_stat.append(max_data)
    mean_data = config.np.mean(new_mas, axis=0)
    list_value_stat.append(mean_data)
    med_data = config.np.median(new_mas, axis=0)
    list_value_stat.append(med_data)
    mode_data = config.scipy.stats.mode(new_mas, axis=0)
    list_value_stat.append(mode_data)
    config.sns.set_theme(style="ticks")
    sns_plot = config.sns.histplot(data=new_mas, binwidth=config.STEP_VALUE, kde=True)
    config.plt.xlabel('Цена ЗП, руб')
    config.plt.ylabel('Количество вакансий')
    config.plt.savefig(config.DISTRIBUTION_FILENAME + str(user_id) + config.DISTRIBUTION_FORMAT)
    config.plt.cla()
    config.plt.clf()
    config.plt.close('all')
    sns_plot.clear()

    return list_value_stat


def doParse(title, area, chat_id):
    jsObj = config.json.loads(getPage(page=0, title=title, area=area))
    pages = jsObj['pages']
    list_title = list()
    list_city = list()
    list_salary = list()
    list_address = list()
    list_metro_station = list()
    list_name_company = list()
    list_date_published = list()
    list_url = list()
    list_logo_url = list()
    list_type_work = list()
    list_dist_salary = list()

    data_currency = config.requests.get(config.currency_href).json()

    if len(jsObj['items']) == 0:
        return 1
    else:
        for page in config.tqdm(range(pages)):
            jsObj = config.json.loads(getPage(page=page, title=title, area=area))
            items = jsObj['items']
            for i in config.tqdm(range(len(items))):
                list_title.append(items[i]['name'])
                list_city.append(items[i]['area']['name'])
                list_salary.append(formedSalary(salary_type=items[i]['salary']))
                list_address.append('Адрес Н/У' if items[i]['address'] is None else items[i]['address']['raw'])
                list_metro_station.append(
                    'Метро Н/У' if items[i]['address'] is None or items[i]['address']['metro'] is None else
                    items[i]['address']['metro']['station_name'])
                list_name_company.append(items[i]['employer']['name'])
                list_date_published.append(items[i]['published_at'])
                list_url.append(items[i]['alternate_url'])

                try:
                    list_logo_url.append(
                        None if items[i]['employer']['logo_urls'] is None else items[i]['employer']['logo_urls'][
                            'original'])
                except:
                    list_logo_url.append('--')
                list_type_work.append(items[i]['schedule']['name'])
                list_dist_salary.append(
                    dist_salary(salary_type=items[i]['salary'], USD_VALUE=data_currency['Valute']['USD'],
                                EUR_VALUE=data_currency['Valute']['EUR']))

        df = config.pd.DataFrame({config.CSV_HEADERS[0]: list_title,
                                  config.CSV_HEADERS[1]: list_city,
                                  config.CSV_HEADERS[2]: list_salary,
                                  config.CSV_HEADERS[3]: list_address,
                                  config.CSV_HEADERS[4]: list_metro_station,
                                  config.CSV_HEADERS[5]: list_name_company,
                                  config.CSV_HEADERS[6]: list_date_published,
                                  config.CSV_HEADERS[7]: list_url,
                                  config.CSV_HEADERS[8]: list_logo_url,
                                  config.CSV_HEADERS[9]: list_type_work})

        df.to_excel(config.CSV_FILENAME + str(chat_id) + config.CSV_FORMAT, engine='xlsxwriter')

        num_vacancies = len(list_title)
        values_stats = form_dist_salary(list_dist_salary=list_dist_salary, step_salary=config.STEP_VALUE, user_id=chat_id)
        values_stats.append(num_vacancies)

        return values_stats
