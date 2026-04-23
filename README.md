# Dashboard de Análise de Voos

Dashboard interativo para análise de dados de voos domésticos nos Estados Unidos.

## Descrição

Este projeto utiliza **Streamlit** para criar um dashboard de visualização de dados de voos. Permite explorar métricas como:
- Número de voos e passageiros por distância
- Top 10 aeroportos mais movimentados
- Rotas mais populares
- Evolução temporal de passageiros
- Distribuição de distâncias

## Requirements

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
```

## Testando o App

Acessar ao Dashboard: (https://dashboard-voos.streamlit.app/)

## Dados

Os dados estão inclusos no arquivo `flights_data.csv` (~180 mil registros, 5% do dataset original)。

| Coluna | Descrição |
|--------|-----------|
| Origin | Código IATA do aeropuerto de origem |
| Destination | Código IATA do aeropuerto de destino |
| Origin City | Cidade de origem |
| Destination City | Cidade de destino |
| Passengers | Número de passageiros |
| Seats | Número de assentos disponíveis |
| Flights | Número de voos |
| Distance | Distância em quilômetros |
| Fly Date | Data do voo (formato AAAAMM) |
| Origin Population | População da cidade de origem |
| Destination Population | População da cidade de destino |