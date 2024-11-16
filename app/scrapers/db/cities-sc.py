import psycopg2
from scrapy.utils.project import get_project_settings
from cities_data import CITIES_DATA

class CitiesSC:
    def __init__(self):
        settings = get_project_settings()
        db = settings.get('DATABASE')

        self._connection = psycopg2.connect(
            host=db['host'], port=db['port'], user=db['username'], password=db['password'], database=db['database']
        )

        self._create_table_query = """
            CREATE TABLE IF NOT EXISTS cities (
                id BIGSERIAL PRIMARY KEY,
                code VARCHAR(7) NOT NULL,
                name VARCHAR(255) NOT NULL
            );
        """

        self._create_table()
        self._insert()

    def _create_table(self):
        try:
            cursor = self._connection.cursor()

            cursor.execute(self._create_table_query)

            self._connection.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            self._connection.rollback()
        finally:
            cursor.close()

    def _insert(self):
        try:
            cursor = self._connection.cursor()

            for statement in CITIES_DATA:
                print('Inserting city into database.')
                cursor.execute(statement)

            self._connection.commit()

            print('All cities inserted.')
        except Exception as e:
            print(f"An error occurred: {e}")
            self._connection.rollback()
        finally:
            cursor.close()
            self._connection.close()

if __name__ == '__main__':
    inserter = CitiesSC()
