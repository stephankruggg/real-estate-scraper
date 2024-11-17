import psycopg2
from scrapy.utils.project import get_project_settings

class CityAndNeighborhoodToRealty:
    def __init__(self):
        settings = get_project_settings()
        db = settings.get('DATABASE')

        self._connection = psycopg2.connect(
            host=db['host'], port=db['port'], user=db['username'], password=db['password'], database=db['database']
        )

        select_cities_query = 'SELECT * FROM cities;'
        select_realties_id_and_location_query = 'SELECT id, location FROM realties;'
        self._select_neighborhoods_by_city_query = 'SELECT * FROM neighborhoods WHERE city_id = %s;'

        self._cursor = self._connection.cursor()

        self._cursor.execute(select_cities_query)
        self._cities_map = {city[2].strip().lower(): city[0] for city in self._cursor.fetchall()}

        self._cursor.execute(select_realties_id_and_location_query)
        self._realties_ids_and_locations = self._cursor.fetchall()

        self._update_neighborhood_query = 'UPDATE realties SET neighborhood_id = %s WHERE id = %s'
        self._update_city_query = 'UPDATE realties SET city_id = %s WHERE id = %s'

        self._fetch_neighborhoods_and_cities()

    def _fetch_neighborhoods_and_cities(self):
        for realty_id, location_data in self._realties_ids_and_locations:
            location_data = location_data.strip().split(', ')

            neighborhood_id = None
            city_id = None

            for location in reversed(location_data):
                location = location.lower()

                if location in self._cities_map:
                        city_id = self._cities_map[location]
                        break

            if not city_id:
                continue

            self._cursor.execute(self._select_neighborhoods_by_city_query, (city_id,))
            neighborhoods = self._cursor.fetchall()

            for location in location_data:
                location = location.lower()

                for neighborhood in neighborhoods:
                    if location == neighborhood[2].strip().lower():
                        neighborhood_id = neighborhood[0]
                        break

            if neighborhood_id:
                self._cursor.execute(self._update_neighborhood_query, (neighborhood_id, realty_id))

            self._cursor.execute(self._update_city_query, (city_id, realty_id))

        self._connection.commit()

if __name__ == '__main__':
    inserter = CityAndNeighborhoodToRealty()
