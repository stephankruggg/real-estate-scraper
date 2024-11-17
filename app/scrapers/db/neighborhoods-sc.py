import psycopg2
from scrapy.utils.project import get_project_settings
from neighborhoods_data import NEIGHBORHOODS_DATA

class neighborhoodsSC:
    def __init__(self):
        settings = get_project_settings()
        db = settings.get('DATABASE')

        self._connection = psycopg2.connect(
            host=db['host'], port=db['port'], user=db['username'], password=db['password'], database=db['database']
        )

        self._create_table_query = """
            CREATE TABLE IF NOT EXISTS neighborhoods (
                id BIGSERIAL PRIMARY KEY,
                code CHAR(10) NOT NULL,
                name VARCHAR(255) NOT NULL,
                city_id BIGINT NOT NULL,
                FOREIGN KEY (city_id) REFERENCES cities(id)
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

            for statement in NEIGHBORHOODS_DATA:
                print('Inserting neighborhood into database.')
                cursor.execute(statement)

            self._connection.commit()

            print('All neighborhoods inserted.')
        except Exception as e:
            print(f"An error occurred: {e}")
            self._connection.rollback()
        finally:
            cursor.close()
            self._connection.close()

if __name__ == '__main__':
    inserter = neighborhoodsSC()