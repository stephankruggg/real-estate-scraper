from typing import Iterable
import scrapy
from scrapy import Request

import re

class ML(scrapy.Spider):
    name = 'ML'
    _headers = { 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'
    }

    _realties_css = 'li.ui-search-layout__item'
    _details_css = 'div > div > div.poly-card__content'
    _location_css = 'span.poly-component__location::text'
    _prices_css = 'div.poly-component__price > div > span > span.andes-money-amount__fraction'
    _collected_realties = []

    def __init__(self) -> None:
        self._base_url = 'https://imoveis.mercadolivre.com.br/venda/santa-catarina/_Desde_{}_NoIndex_True'
        self._limit = 146

    def start_requests(self) -> Iterable[Request]:
        for page in range(1, self._limit + 1, 48):
            yield Request(url = self._base_url.format(page), callback = self._get_all_in_page, headers = self._headers)
    
    def _get_all_in_page(self, response):
        for realty in response.css(self._realties_css):
            details = realty.css(self._details_css)

            content = details.css('span::text').get()
            if re.search(r'\bterreno?\b', content, re.IGNORECASE):
                continue

            url = details.css('h2 > a')
            facilities = self._get_facilities(details)
            prices = details.css(self._prices_css)

            obj = {
                'name': url.css('::text').get(),
                'url': url.css('::attr(href)').get(),
                'price': float(prices.css('::text').get().replace('.', '').replace(',', '.')),
                'condominium': None,
                'iptu': None,
                'bedrooms': facilities['bedrooms'],
                'bathrooms': facilities['bathrooms'],
                'garage_spaces': None,
                'square_meters': facilities['square_meters'],
                'location': details.css(self._location_css).get()
            }

            self._collected_realties.append(obj)

            yield obj

    def _get_facilities(self, details):
        facilities = {
            'bedrooms': None,
            'bathrooms': None,
            'square_meters': None
        }

        regexes = {
            'bedrooms': r'\bquartos?\b',
            'bathrooms': r'\bbanheiros?\b',
            'square_meters': r'\bm²?\b'
        }

        for facility in details.css('div.poly-component__attributes-list > ul > li'):
            facility = facility.css('::text').get()

            for facility_type in facilities.keys():
                if not re.search(regexes[facility_type], facility, re.IGNORECASE):
                    continue

                amount = re.search(r'\d+', facility)
                if not amount:
                    continue
                amount = amount.group()

                facilities[facility_type] = amount

        return facilities
