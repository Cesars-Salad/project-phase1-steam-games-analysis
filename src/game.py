# imports
import os
import csv
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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


# fase 2

# Extracao e leitura do steam_games.csv
def load_and_extract_games_to_df(zip_path, extract_to):
    csv_path = os.path.join(extract_to, "steam_games.csv")
    
    if not os.path.exists(csv_path):
        print(f"Extraindo {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Arquivo extraído para {extract_to}")
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo {csv_path} não encontrado após extração.")
    
    df = pd.read_csv(csv_path)
    df.columns = [col.replace(" ", "_") for col in df.columns]  # Remover espaços das colunas
    df = df.drop_duplicates(subset=["Name"])
    df = df.dropna(how='all')
    return df

# Pergunta 1: Top 10 jogos mais bem avaliados

def top_10_metacritic(df):
    df_valid = df.dropna(subset=["Metacritic_score", "Release_date"])
    df_valid["Metacritic_score"] = df_valid["Metacritic_score"].astype(int)
    df_valid["Ano"] = df_valid["Release_date"].apply(lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan)
    df_valid = df_valid.dropna(subset=["Ano"]).sort_values(by=["Metacritic_score", "Ano"], ascending=[False, True])
    return df_valid[["Name", "Metacritic_score", "Ano"]].head(10).to_string(index=False)

# Pergunta 2: Estatísticas para jogos de Role-Playing

def rpg_stats(df):
    df_rpg = df[df["Genres"].str.contains("RPG", na=False)].copy()
    df_rpg.loc[:, "Demo_mat"] = df_rpg["Screenshots"].str.count(",") + df_rpg["Movies"].str.count(",") + 2
    
    stats = pd.DataFrame({
        "Média": df_rpg[["DLC_count", "Positive", "Negative", "Demo_mat"]].mean(),
        "Máximo": df_rpg[["DLC_count", "Positive", "Negative", "Demo_mat"]].max()
    })
    return stats.to_string()

# Pergunta 3: Empresas que mais publicam jogos pagos

def top_publishers(df):
    df_paid = df[df["Price"] > 0]
    df_publishers = df_paid.explode("Publishers").groupby("Publishers").size().nlargest(5)
    df_stats = df_paid[df_paid["Publishers"].isin(df_publishers.index)].groupby("Publishers")["Positive"].agg(["mean", "median"])
    return df_publishers.to_frame(name="Jogos Publicados").join(df_stats).to_string()

# Pergunta 4: Crescimento de jogos para Linux

def linux_growth(df):
    # Filtrando os dados para considerar apenas os lançamentos para Linux
    df_linux = df[df["Linux"] == True].copy()
    
    # Extraindo o ano da coluna 'Release_date'
    df_linux.loc[:, "Ano"] = df_linux["Release_date"].apply(
        lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan
    )
    
    # Removendo linhas com valor 'Ano' nulo e agrupando por ano
    df_years = df_linux.dropna(subset=["Ano"]).groupby("Ano").size()
    
    # Filtrando os dados para os anos entre 2018 e 2022
    df_recent = df_years.loc[2018:2022]
    
    # Calculando as variações anuais
    variacoes = df_recent.diff().dropna()
    
    # Calculando a tendência de crescimento ou declínio
    tendencia = variacoes.mean()
    
    # Formatar o DataFrame de anos recentes em uma string mais legível
    crescimento = df_recent.to_string(index=True)
    
    # Definindo a descrição do crescimento ou declínio
    if tendencia > 0:
        tendencia_texto = f"O crescimento de lançamentos para Linux entre 2018 e 2022 é positivo:\n Em média há um crescimento de {tendencia:.2f} novos jogos a cada ano além do número do ano anterior."
    else:
        tendencia_texto = f"O crescimento de lançamentos para Linux entre 2018 e 2022 é negativo:\n Em média há um decréscimo de {tendencia:.2f} novos jogos a cada ano abaixo do número do ano anterior."
    
    # Retorna o resultado formatado
    return f"Dados de lançamentos de Linux por ano:\n{crescimento}\n\n{tendencia_texto}"


# Pergunta 5: Categoria com maior base de jogadores

def top_category(df):
    df["Owners"] = df["Estimated_owners"].str.split("-").str[1].astype(float)
    df_exp = df.explode("Categories").groupby("Categories")["Owners"].sum().nlargest(10)
    return f"Total de categorias analisadas: {df_exp.shape[0]}\n{df_exp.to_string()}"

# Gráfico 1: Percentual de suporte por sistema operacional

def os_support_chart(df):
    os_counts = df[["Windows", "Mac", "Linux"]].sum()
    os_counts.plot.pie(autopct="%.1f%%", labels=["Windows", "Mac", "Linux"], colors=["blue", "gray", "green"], title="Suporte por Sistema Operacional")
    plt.show()

# Gráfico 2: Tendência de lançamentos de jogos Indie e Estratégia
def indie_strategy_trend(df):
    
    # Filtra os dados para o ano de 2010 a 2020
    df_filtered = df[(df["Categories"].str.contains("Single-player", na=False)) & df["Genres"].str.contains("Indie|Strategy", na=False)].copy()
    
    # Cria a coluna "Ano"
    df_filtered.loc[:, "Ano"] = df_filtered["Release_date"].apply(lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan)
    
    # Filtra os dados apenas para os anos de 2010 a 2020
    df_filtered = df_filtered[df_filtered["Ano"].between(2010, 2020, inclusive='both')]
    
    # Conta a quantidade de "Indie" e "Strategy" para cada ano
    indie_count = df_filtered[df_filtered["Genres"].str.contains("Indie", na=False)].groupby("Ano").size()
    strategy_count = df_filtered[df_filtered["Genres"].str.contains("Strategy", na=False)].groupby("Ano").size()

    # Junta os dois contadores em um df
    df_counts = pd.DataFrame({
        "Indie": indie_count,
        "Strategy": strategy_count
    }).fillna(0)  # Substitui valores ausentes por 0
    
    # Criação do gráfico de barras
    ax = df_counts.plot(kind='bar', figsize=(10, 6), width=0.8)
    plt.title('Contagem de gêneros "Indie" e "Strategy" de 2010 a 2020')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade de Jogos Lançados')
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    fontsize=10, color='black', 
                    xytext=(0, 8), textcoords='offset points')

    # Exibir a legenda para identificar os gêneros
    plt.legend(title="Gêneros", loc='upper left')
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.show()

# Gráfico 3: Tendência de categorias ao longo dos anos

def category_trend(df):  
    df_filtered_trend = df[df["Categories"].str.contains("Single-player|Multi-player", na=False)].copy()

    # Extraindo o ano da coluna 'Release_date'
    df_filtered_trend.loc[:, "Ano"] = df_filtered_trend["Release_date"].apply(lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan)

    # Filtrando os dados para os anos entre 2010 e 2022
    df_filtered_trend = df_filtered_trend[df_filtered_trend["Ano"].between(2010, 2022)]

    # Contagem de jogos 'Single-player', excluindo os 'Multi-player'
    single_count = df_filtered_trend[
        df_filtered_trend["Categories"].str.contains("Single-player", na=False) &
        ~df_filtered_trend["Categories"].str.contains("Multi-player", na=False)
    ].groupby("Ano").size()

    # Contagem de jogos 'Multi-player'
    multi_count = df_filtered_trend[
        df_filtered_trend["Categories"].str.contains("Multi-player", na=False)
    ].groupby("Ano").size()

    df_counts_trend = pd.DataFrame({
            "Single-player": single_count,
            "Multi-player": multi_count
        }).fillna(0)

    # Criação do gráfico de barras
    ax = df_counts_trend.plot(kind='bar', figsize=(10, 6), width=0.8)
    plt.title('Tendência de jogos para um jogador ou multijogador entre 2010 e 2022')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade de Jogos Lançados')
    for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        fontsize=10, color='black', 
                        xytext=(0, 8), textcoords='offset points')

        # Exibir a legenda para identificar os gêneros
    plt.legend(title="Categorias", loc='upper left')
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.show()
