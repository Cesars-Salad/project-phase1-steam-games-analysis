# imports
import os
import csv
import zipfile
from collections import Counter # ver comentarios em metodo estatico 2
from datetime import datetime # ver comentarios em metodo estatico 2 

# definicao da classe Game buscando o cabecalho das colunas no proprio arquivo
class Game:
    def __init__(self, **attributes):
        for key, value in attributes.items():
            key = key.replace(' ', '_') # substituicao dos espacos do cabecalho por "_" para garantir que possamos usar esses metodos de classe no ambiente python
            setattr(self, key, self._convert_value(value))

    # garantir a formatacao dos dados numericos
    def _convert_value(self, value):
        value = value.strip()
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value
    
    def __str__(self):
        return str(self.__dict__)

    # metodo estatico 1 para resolver a questao do do percentual de jogos gratuitos
    @staticmethod
    def percentual_gratuitos(jogos):
        total_jogos = len(jogos)
        jogos_gratuitos = sum(1 for jogo in jogos if jogo.Price == 0.0)
        percentual = (jogos_gratuitos / total_jogos) * 100
        return f"{percentual:.2f}%"

    # metodo estatico 2 para resolver a questao do ano com maior numero de lancamentos de jogos
    @staticmethod
    def ano_maior_numero_lancamentos(jogos):
        anos = []
        for jogo in jogos: # aqui vamos usar um pouco de tratamento de dados para garantir a extracao correta dos anos, mas sinta-se a vontade para usar outros metodos para esse tratamento
            data = jogo.Release_date
            if data:
                try:
                    ano = datetime.strptime(data, '%b %d, %Y').year # se voce nao quiser usar datetime no processamento das datas tambem é possivel usar um metodo mais simples 
                except ValueError:                                  # as datas tem um padrao (normalmente) de "mmm dd aaaa", entao poderiamos extrair os 4 ultimos caracteres da string
                    try:                                            # contudo o uso de datetime vai buscar adequadamente por valores de data
                        ano = datetime.strptime(data, '%b %Y').year
                    except ValueError:
                        continue
                anos.append(ano)
                # ate a linha anterior voce poderia separar essa def em duas defs caso precise reaproveitar a lista anos em outras analises a fim de evitar consumo computacional
        contagem_anos = Counter(anos) #  subclasse do dicionário em Python, mas se voce nao quiser usar tambem é possivel fazer a contagem por um laco "for"
        max_lancamentos = max(contagem_anos.values())
        return [ano for ano, count in contagem_anos.items() if count == max_lancamentos]

    # metodo estatico 3 
    @staticmethod
    def top_5_jogos_com_mais_usuarios(jogos):
        jogos_ordenados = sorted(jogos, key=lambda jogo: jogo.Peak_CCU, reverse=True)[:5]
        resultado = []
        for jogo in jogos_ordenados:
            percentual_avaliacoes = (jogo.Positive / (jogo.Positive + jogo.Negative) * 100) if (jogo.Positive + jogo.Negative) > 0 else 0
            resultado.append({
                "Nome": jogo.Name,
                "Pico de Jogadores": jogo.Peak_CCU,
                "Percentual de Avaliações Positivas": f"{percentual_avaliacoes:.2f}%",
                "Tempo Médio de Jogo": f"{jogo.Average_playtime_forever} horas"
            })
        return resultado

# Extracao e leitura do steam_games.csv

def load_and_extract_games(zip_path, extract_to):
    # Caminho completo do arquivo CSV extraído
    csv_path = os.path.join(extract_to, "steam_games.csv")
    
    # Verifica se o arquivo CSV já foi extraído, caso contrário, extrai o zip
    if not os.path.exists(csv_path):
        print(f"Extraindo {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Arquivo extraído para {extract_to}")
    
    # Agora faz a leitura do CSV
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo {csv_path} não encontrado após extração.")
    
    games = []
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            games.append(Game(**row))
    
    return games
