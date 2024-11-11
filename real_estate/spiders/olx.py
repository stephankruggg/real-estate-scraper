from typing import Iterable
import scrapy
from scrapy import Request

import re

class Olx(scrapy.Spider):
    name = 'OLX'
    _headers = { 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'
    }

    _realties_css = 'div.olx-ad-card__content.olx-ad-card__content--horizontal'
    _details_css = 'div.olx-ad-card__top > div.olx-ad-card__details-ads'
    _location_css = 'div.olx-ad-card__bottom > div > div > div > p::text'
    _prices_css = 'div.olx-ad-card__top > div.olx-ad-card__details-price--horizontal'
    _collected_realties = []

    def __init__(self) -> None:
        self._base_url = 'https://www.olx.com.br/imoveis/venda/estado-sc?o={}'
        self._limit = 1

    def start_requests(self) -> Iterable[Request]:
        for page in range(1, self._limit + 1):
            yield Request(url = self._base_url.format(page), callback = self._get_all_in_page, headers = self._headers)
    
    def _get_all_in_page(self, response):
        for realty in response.css(self._realties_css):
            details = realty.css(self._details_css)

            url = details.css('a')
            facilities = self._get_facilities(details)
            prices = realty.css(self._prices_css)
            extra_prices = self._get_extra_prices(prices)

            obj = {
                'name': url.css('h2::text').get(),
                'url': url.css('::attr(href)').get(),
                'price': float(prices.css('h3::text').get().replace('R$', '').replace('.', '').replace(',', '.')),
                'condominium': extra_prices['condominium'],
                'iptu': extra_prices['iptu'],
                'bedrooms': facilities['bedrooms'],
                'bathrooms': facilities['bathrooms'],
                'garage_spaces': facilities['garage_spaces'],
                'square_meters': facilities['square_meters'],
                'location': realty.css(self._location_css).get()
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
            'bathrooms': r'\bbanheiros?\b',
            'garage_spaces': r'\bvagas?\b',
            'square_meters': r'\bmetros?\b'
        }

        for facility in details.css('ul > li'):
            facility = facility.css('span::attr(aria-label)').get()

            for facility_type in facilities.keys():
                if not re.search(regexes[facility_type], facility, re.IGNORECASE):
                    continue

                amount = re.search(r'\d+', facility)
                if not amount:
                    continue
                amount = amount.group()

                facilities[facility_type] = amount

        return facilities

    def _get_extra_prices(self, prices):
        extra_prices = {
            'iptu': None,
            'condominium': None
        }

        regexes = {
            'iptu': r'\biptu?\b',
            'condominium': r'\bcondomínio?\b'
        }

        prices = prices.css('div > p')
        for price in prices:
            price = price.css('::text').get()

            for price_type in extra_prices.keys():
                if not re.search(regexes[price_type], price, re.IGNORECASE):
                    continue

                amount = re.search(r'\d+', price)
                if not amount:
                    continue
                amount = amount.group()

                extra_prices[price_type] = float(amount.replace('.', '').replace(',', '.'))

        return extra_prices
