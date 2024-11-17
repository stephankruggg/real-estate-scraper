from settings import DATABASE
import psycopg2

if __name__ == '__main__':
    print('Bem-vindo ao consultor de imóveis!')

    while True:
        city_name = input('Informe uma cidade para a busca de imóveis à venda: ')
        if not city_name:
            print('Nenhuma cidade informada.')
            continue

        neighborhood_name = input('Informe um bairro. Caso não deseje informar, basta pressionar ENTER: ')

        bedrooms = input('Informe o número de quartos. Caso não deseje informar, basta pressionar ENTER: ')
        bathrooms = input('Informe o número de banheiros. Caso não deseje informar, basta pressionar ENTER: ')
        garage_spaces = input('Informe o número de vagas de garagem. Caso não deseje informar, basta pressionar ENTER: ')

        db = DATABASE
        connection = psycopg2.connect(
            host=db['host'], port=db['port'], user=db['username'], password=db['password'], database=db['database']
        )

        cursor = connection.cursor()

        city_select_query = 'SELECT id FROM cities WHERE name = %s'
        cursor.execute(city_select_query, (city_name,))
        city_ids = cursor.fetchall()

        if len(city_ids) == 0:
            print('Nenhuma cidade com esse nome encontrada.')
            continue

        city_id = city_ids[0]
        select_params = [city_id]
        realties_select_query = 'SELECT * FROM realties WHERE city_id = %s'

        if neighborhood_name:
            neighborhood_select_query = 'SELECT id FROM neighborhoods WHERE city_id = %s and name = %s'
            cursor.execute(neighborhood_select_query, (city_id, neighborhood_name))
            neighborhood_ids = cursor.fetchall()

            if len(neighborhood_ids) == 0:
                print('Nenhum bairro com esse nome encontrado.')
                continue

            select_params.append(neighborhood_ids[0])
            realties_select_query += ' AND neighborhood_id = %s'

        if bedrooms:
            select_params.append(int(bedrooms))
            realties_select_query += ' AND bedrooms = %s'

        if bathrooms:
            select_params.append(int(bathrooms))
            realties_select_query += ' AND bathrooms = %s'

        if garage_spaces:
            select_params.append(int(garage_spaces))
            realties_select_query += ' AND garage_spaces = %s'

        realties_select_query += ' ORDER BY price ASC'
        cursor.execute(realties_select_query, tuple(select_params))

        realties = cursor.fetchall()

        total_prices = 0
        for i, realty in enumerate(realties):
            print(f'Imóvel {i + 1}')

            print(f'Postagem: {realty[1]}')
            print(f'URL: {realty[2]}')
            print(f'Preço: {realty[3]}')

            if realty[4]:
                print(f'IPTU: {realty[4]}')

            if realty[5]:
                print(f'Condomínio: {realty[5]}')

            if realty[6]:
                print(f'Número de quartos: {realty[6]}')

            if realty[7]:
                print(f'Número de banheiros: {realty[7]}')

            if realty[8]:
                print(f'Vagas de garagem: {realty[8]}')

            if realty[9]:
                print(f'Metragem quadrada: {realty[9]}')

            total_prices += realty[3]

        print(f'Preço médio dos imóveis: R${total_prices // len(realties)}')
