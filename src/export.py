import csv
import random
import os
from openpyxl import Workbook

def export_to_excel(csv_path, excel_output, seed=69):
    if os.path.exists(excel_output):
        print(f"Arquivo {excel_output} já existe. Nenhuma ação realizada.")
        return
    
    random.seed(seed)
    
    # Leitura do CSV
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        header, data = reader[0], reader[1:]
        selected_rows = random.sample(data, min(20, len(data)))
    
    # Criação do arquivo Excel (.xlsx)
    wb = Workbook()
    ws = wb.active
    ws.title = "Dados Selecionados"
    
    # Escreve o header na primeira linha
    ws.append(header)
    
    # Adiciona as 20 linhas aleatorias
    for row in selected_rows:
        ws.append(row)
    
    # Salva o arquivo
    wb.save(excel_output)
    
    print(f"Arquivo exportado para {excel_output}")
