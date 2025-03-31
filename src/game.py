# imports
import os
import csv
import zipfile
import pandas as pd # fase 2
import numpy as np #fase 2
import matplotlib.pyplot as plt # fase 2

from collections import Counter # ver comentarios em metodo estatico 2
from datetime import datetime # ver comentarios em metodo estatico 2 

# fase 1
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
    df_linux = df[df["Linux"] == True].copy()
    
    df_linux.loc[:, "Ano"] = df_linux["Release_date"].apply(
        lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan
    )

    df_years = df_linux.dropna(subset=["Ano"]).groupby("Ano").size()
    
    df_recent = df_years.loc[2018:2022]

    variacoes = df_recent.diff().dropna()
    
    tendencia = variacoes.mean()
    
    crescimento = df_recent.to_string(index=True)
    
    # Definindo a descrição do crescimento ou declínio
    if tendencia > 0:
        tendencia_texto = f"O crescimento de lançamentos para Linux entre 2018 e 2022 é positivo:\n Em média há um crescimento de {tendencia:.2f} novos jogos a cada ano acima do número do ano anterior."
    else:
        tendencia_texto = f"O crescimento de lançamentos para Linux entre 2018 e 2022 é negativo:\n Em média há um decréscimo de {tendencia:.2f} novos jogos a cada ano abaixo do número do ano anterior."
    
    # Retorna o resultado formatado
    return f"Dados de lançamentos de Linux por ano:\n{crescimento}\n\n{tendencia_texto}"


# Pergunta 5: Categoria com maior base de jogadores

def calculate_avg_owners(owner_range):
    # Extrair os números do formato '(min - max)'
    min_owners, max_owners = map(int, owner_range.split(' - '))
    return (min_owners + max_owners) / 2 # estimativa do numero de owners sera a media entre max e min, mas um RNG entre os ranges também poderia ser valido

# def em comum 2

def human_readable(num):
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"  # Para milhões
    elif num >= 1_000:
        return f"{num / 1_000:.1f}k"  # Para milhares
    else:
        return f"{num:.0f}"  # Para números abaixo de 1.000
    
# parte 1 da pergunta

def pergunta_parte_1(df):
    df['Average_owners'] = df['Estimated_owners'].apply(calculate_avg_owners)
    df_expanded_1 = df.explode('Genres')
    genre_owners_1 = df_expanded_1.groupby('Genres')['Average_owners'].sum().reset_index()
    genre_owners_sorted_1 = genre_owners_1.sort_values(by='Average_owners', ascending=False).reset_index(drop=True)
    genre_owners_sorted_1['Average_owners'] = genre_owners_sorted_1['Average_owners'].apply(human_readable)
    print(genre_owners_sorted_1.head(20).to_string(index=False))
    
# parte 2 da pergunta

def pergunta_parte_2(df):
    df['Average_owners'] = df['Estimated_owners'].apply(calculate_avg_owners)
    df_expanded_2 = df.assign(Genres=df['Genres'].str.split(',')).explode('Genres')
    df_expanded_2['Genres'] = df_expanded_2['Genres'].str.strip()  # Remover espaços extras
    genre_owners_2 = df_expanded_2.groupby('Genres')['Average_owners'].sum().reset_index()
    genre_owners_sorted_2 = genre_owners_2.sort_values(by='Average_owners', ascending=False).reset_index(drop=True)
    genre_owners_sorted_2['Average_owners'] = genre_owners_sorted_2['Average_owners'].apply(human_readable)
    print(genre_owners_sorted_2.head(20).to_string(index=False))


# Gráfico 1: Percentual de suporte por sistema operacional

def os_support_chart(df):
    os_counts = df[["Windows", "Mac", "Linux"]].sum()
    colors = plt.cm.Paired([0, 2, 4])
    os_counts.plot.pie(autopct="%.1f%%", labels=["Windows", "Mac", "Linux"], colors=colors, title="Suporte por Sistema Operacional")
    plt.show()

# Gráfico 2: Tendência de lançamentos de jogos Indie e Estratégia
def indie_strategy_trend(df):
    
    df_filtered = df[(df["Categories"].str.contains("Single-player", na=False)) & df["Genres"].str.contains("Indie|Strategy", na=False)].copy()
    
    df_filtered.loc[:, "Ano"] = df_filtered["Release_date"].apply(lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan)
    
    df_filtered = df_filtered[df_filtered["Ano"].between(2010, 2020, inclusive='both')]
    
    indie_count = df_filtered[df_filtered["Genres"].str.contains("Indie", na=False)].groupby("Ano").size()
    strategy_count = df_filtered[df_filtered["Genres"].str.contains("Strategy", na=False)].groupby("Ano").size()

    df_counts = pd.DataFrame({
        "Indie": indie_count,
        "Strategy": strategy_count
    }).fillna(0)  
    
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

    plt.legend(title="Gêneros", loc='upper left')
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.show()


# Gráfico 3: Tendência de categorias ao longo dos anos

def category_trend(df):  
    df_filtered_trend = df[df["Categories"].str.contains("Single-player|Multi-player", na=False)].copy()
    df_filtered_trend.loc[:, "Ano"] = df_filtered_trend["Release_date"].apply(lambda x: int(str(x)[-4:]) if isinstance(x, str) and len(str(x)) >= 4 else np.nan)
    df_filtered_trend = df_filtered_trend[df_filtered_trend["Ano"].between(2010, 2022)]
    single_count = df_filtered_trend[
        df_filtered_trend["Categories"].str.contains("Single-player", na=False) &
        ~df_filtered_trend["Categories"].str.contains("Multi-player", na=False)
    ].groupby("Ano").size()

    multi_count = df_filtered_trend[
        df_filtered_trend["Categories"].str.contains("Multi-player", na=False)
    ].groupby("Ano").size()

    df_counts_trend = pd.DataFrame({
            "Single-player": single_count,
            "Multi-player": multi_count
        }).fillna(0)

    ax = df_counts_trend.plot(kind='bar', figsize=(10, 6), width=0.8, color=['#FF5733', '#33FF57'])
    plt.title('Tendência de jogos para um jogador ou multijogador entre 2010 e 2022')
    plt.xlabel('Ano')
    plt.ylabel('Quantidade de Jogos Lançados')
    for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', 
                        fontsize=10, color='black', 
                        xytext=(0, 8), textcoords='offset points')

    plt.legend(title="Categorias", loc='upper left')
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.show()


# grafico 4: densidade de jogos relacionando preço e avaliacao de usuarios 
# FIXME: esse seria um gráfico para fazer uma densidade de jogos relacionando preco e avaliacoes, mas requer otimizacao para funcionar adequadamente
"""""
def density_price_vs_positive(df):
    df_density_price = df[['Price', 'Positive', 'Negative']].copy()
    df_density_price.loc[:, 'Positive_Percentage'] = df_density_price['Positive'] / (df_density_price['Positive'] + df_density_price['Negative']) * 100
    
    with sns.axes_style('whitegrid'):

        grafico = sns.pairplot(data=df_density_price, palette="pastel")
"""""