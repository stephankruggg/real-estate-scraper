from typing import Iterable
import scrapy
from scrapy import Request

import re

class ImoveisSC(scrapy.Spider):
    name = 'ImóveisSC'
    _headers = { 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'
    }

    _realties_css = 'div.lista-imoveis > article'
    _details_css = 'div.imovel-data'
    _price_css = 'span.imovel-preco'
    _header_css = 'header'
    _collected_realties = []

    def __init__(self) -> None:
        self._base_url = 'https://www.imoveis-sc.com.br/todas-cidades/comprar?page={}'
        self._limit = 15

    def start_requests(self) -> Iterable[Request]:
        for page in range(1, self._limit + 1):
            yield Request(url = self._base_url.format(page), callback = self._get_all_in_page, headers = self._headers)
    
    def _get_all_in_page(self, response):
        for realty in response.css(self._realties_css):
            details = realty.css(self._details_css)

            header = details.css(self._header_css)
            facilities = self._get_facilities(details)
            price = details.css(self._price_css)

            obj = {
                'name': header.css('h2 > a::text').get().strip(),
                'url': header.css('h2 > a::attr(href)').get(),
                'price': float(price.css('small::text').get().replace('.', '').replace(',', '.')),
                'condominium': None,
                'iptu': None,
                'bedrooms': facilities['bedrooms'],
                'bathrooms': facilities['bathrooms'],
                'garage_spaces': facilities['garage_spaces'],
                'square_meters': facilities['square_meters'],
                'location': header.css('div > strong::text').get()
            }

            self._collected_realties.append(obj)

            yield obj

    def _get_facilities(self, details):
        facilities = {
            'bedrooms': None,
            'bathrooms': None,
            'garage_spaces': None,
            'square_meters': None
        }

        regexes = {
            'bedrooms': r'\bquartos?\b',
            'bathrooms': r'\bsuítes?\b',
            'garage_spaces': r'\bvagas?\b',
            'square_meters': r'\bm²\b'
        }

        for facility in details.css('ul > li'):
            facility = facility.css('span')

            for facility_type in facilities.keys():
                if not re.search(regexes[facility_type], facility.css('span::text').get().strip(), re.IGNORECASE):
                    continue

                amount = re.search(r'\d+', facility.css('strong::text').get())
                if not amount:
                    continue
                amount = amount.group()

                facilities[facility_type] = int(amount)

        return facilities
