import requests

import settings


class CompaniesNotFoundError(Exception):
    pass


def get_company_names(query):
    params = {
        "apikey": settings.API_KEY,
        "text": query,
        "lang": "ru_RU",
        "type": "biz"
    }
    response = requests.get(settings.SEARCH_COMPANY_API_SERVER, params=params)
    if not response:
        raise CompaniesNotFoundError

    json_response = response.json()
    company_names = []
    for company in json_response['features']:
        company_names.append(company["properties"]["CompanyMetaData"]["name"])

    return company_names


if __name__ == "__main__":
    print(get_company_names('Екатеринбург улица Чекистов 5'))
