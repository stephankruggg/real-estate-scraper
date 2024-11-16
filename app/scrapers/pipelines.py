import logging
import psycopg2
from psycopg2 import sql
from scrapy.utils.project import get_project_settings

class RealEstatePipeline:
    def __init__(self):
        settings = get_project_settings()
        db = settings.get('DATABASE')

        self._connection = psycopg2.connect(
            host=db['host'], port=db['port'], user=db['username'], password=db['password'], database=db['database']
        )

        self._cursor = self._connection.cursor()

        self._create_realties_table()

        logging.info("Database connection established")

    def _create_realties_table(self):
        create_realties_query = """
            CREATE TABLE IF NOT EXISTS realties (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                price NUMERIC NOT NULL,
                condominium NUMERIC,
                iptu NUMERIC,
                bedrooms INTEGER,
                bathrooms INTEGER,
                garage_spaces INTEGER,
                square_meters INTEGER,
                location TEXT NOT NULL,
                city_id INTEGER,
                neighborhood_id INTEGER,
                FOREIGN KEY (city_id) REFERENCES cities(id),
                FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(id)
            );
        """

    def process_item(self, item, spider):
        logging.info(f"Processing item: {item}")

        insertion_query = sql.SQL("""
            INSERT INTO realties (name, url, price, condominium, iptu, bedrooms, bathrooms, garage_spaces, square_meters, location)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """)

        values = (
            item['name'],
            item['url'],
            item['price'],
            item['condominium'],
            item['iptu'],
            int(item['bedrooms'] or 0),
            int(item['bathrooms'] or 0),
            int(item['garage_spaces'] or 0),
            int(item['square_meters'] or 0),
            item['location']
        )

        try:
            self._cursor.execute(insertion_query, values)
            self._connection.commit()
            logging.info("Item successfully inserted into database")
        except psycopg2.DatabaseError as e:
            spider.logger.error(f"Database error: {e}")
            self._connection.rollback()

    def close(self):
        self._cursor.close()
        self._connection.close()
