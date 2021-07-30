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


def doParse(title, area):
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
    for page in range(pages):
        jsObj = config.json.loads(getPage(page=page, title=title, area=area))
        items = jsObj['items']
        for i in range(len(items)):
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

    df.to_excel(config.CSV_FILENAME, engine='xlsxwriter')
