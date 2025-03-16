import csv
import random
import os

def export_to_excel(csv_path, excel_path, seed=69):
    if os.path.exists(excel_path):
        print(f"Arquivo {excel_path} já existe. Nenhuma ação realizada.")
        return
    
    random.seed(seed)
    
    with open(csv_path, "r", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        header, data = reader[0], reader[1:]
        selected_rows = random.sample(data, min(20, len(data)))
    
    with open(excel_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(selected_rows)
    
    print(f"Arquivo exportado para {excel_path}")