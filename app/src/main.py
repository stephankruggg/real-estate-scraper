from settings import DATABASE
import psycopg2
import locale
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
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

        realties = pd.DataFrame(
            cursor.fetchall(),
            columns=['ID', 'Postagem', 'URL', 'Preço', 'IPTU', 'Condomínio', '# Quartos', '# Banheiros', '# Vagas de garagem', 'Metragem quadrada', 'Localização', 'ID cidade', 'ID bairro']
        )

        total_prices = 0
        for i, realty in realties.iterrows():
            print(f'Imóvel {i + 1}')

            print(f'Postagem: {realty['Postagem']}')
            print(f'URL: {realty['URL']}')

            print(f'Preço: R${locale.format_string('%.2f', realty['Preço'], grouping=True)}')

            if realty[4]:
                print(f'IPTU: R${locale.format_string('%.2f', realty['IPTU'], grouping=True)}')

            if realty[5]:
                print(f'Condomínio: R${locale.format_string('%.2f', realty['Condomínio'], grouping=True)}')

            if realty[6]:
                print(f'Número de quartos: {realty['# Quartos']}')

            if realty[7]:
                print(f'Número de banheiros: {realty['# Banheiros']}')

            if realty[8]:
                print(f'Vagas de garagem: {realty['# Vagas de garagem']}')

            if realty[9]:
                print(f'Metragem quadrada: {realty['Metragem quadrada']}')

                print(f'Preço por metro quadrado: R${locale.format_string('%.2f', realty['Preço'] / realty['Metragem quadrada'], grouping=True)}')

            total_prices += realty[3]

        if not bedrooms:
            plt.scatter(realties['# Quartos'], realties['Preço'])
            plt.xlabel('Número de quartos')
            plt.ylabel('Preço')
            plt.savefig('imgs/preco_vs_#_quartos.png', bbox_inches='tight')
            plt.close()

        sns.histplot(data=realties, x='Preço', bins=30, kde=True)
        max_y = int(plt.gca().get_ylim()[1])
        plt.yticks(range(0, max_y + 1))
        plt.ylabel('Quantidade')
        plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'R${x / 1e6:.1f}M'))
        plt.savefig('imgs/distribuicao_precos.png', bbox_inches='tight')
        plt.close()

        wordcloud = WordCloud().generate(' '.join(realties['Postagem']))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig('imgs/nuvem_de_palavras.png', bbox_inches='tight')
        plt.close()

        average_price = total_prices // len(realties)
        print(f'Preço médio dos imóveis: R${locale.format_string('%.2f', average_price, grouping=True)}')
