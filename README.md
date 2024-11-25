# real-estate-scraper

Este é um projeto realizado para a disciplina de Tópicos Especiais em Gerência de Dados (INE5454). Consiste de web scrapers utilizados para coletar dados de imóveis à venda no estado de Santa Catarina, de forma a exemplificar o funcionamento de extração de dados a partir de fontes externas.

## Web scraping
Os sites coletados foram:
- OLX
- Imóveis SC
- Mercado Livre

Para executar os scrapers basta executar o seguinte comando em um terminal:

``` bash
cd app && scrapy crawl '<crawler-name>' && cd .. 
```

Em que <crawler-name> deve ser substituído pelos possíves nomes para crawlers:
- OLX
- ImóveisSC
- ML

## Dados

Os dados serão salvos utilizando o SGBD Postgresql, no banco real_estate. A criação deste deve ser realizada previamente, com as informações de conexão configuradas no arquivo de settings:
https://github.com/stephankruggg/real-estate-scraper/blob/4e434d2d335770a62cb3cfcb5a6a95c89d2e057d/app/scrapers/settings.py#L95-L101

Alternativamente é possível utilizar o dump do SQL disponível em:
https://github.com/stephankruggg/real-estate-scraper/blob/4e434d2d335770a62cb3cfcb5a6a95c89d2e057d/app/scrapers/db/real_estate.sql

Além disso, o banco de dados utilizado no projeto foi acrescido de informações de bairros e cidades do estado de Santa Catarina provenientes do IBGE. Para realizar a inserção desses dados no seu banco de dados, é possível executar os seguintes comandos:

``` bash
cd app/scrapers/db
python cities-sc.py
python neighborhoods-sc.py
python city_and_neighborhood_to_realty.py
cd ../../..
```

Obs.: O dump já possui essas informações acrescidas.

## Aplicação

Foi realizada a criação de uma aplicação simples para simular um desenvolvimento com base nos dados coletados. Essa aplicação permite que o usuário passe informações do imóvel que deseja comprar (ex.: cidade, bairro, número de quartos etc.) e a aplicação responderá com os imóveis que se adequam à sua busca, além de informações extras que auxiliem na tomada de decisão:
- Preço por metro quadrado
- Preço médio dos imóveis
- Histograma com a distribuição de preços
- Nuvem de palavras das postagens de imóveis
- Relação de preço por número de quartos, caso o usuário não especifique o número de quartos do imóvel desejado

Dessa forma, o usuário pode tomar uma decisão mais adequada comparando dados de maneira facilitada.
