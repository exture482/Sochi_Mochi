import pandas as pd
import numpy as np

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    
    cloud_columns = [col for col in df.columns if 'Облачность' in col]
    valid_cloud_types = ['Ясно', 'Малооблачно', 'Переменная облачность', 'Пасмурно']
    for col in cloud_columns:
        for cloud_type in valid_cloud_types:
            df[f"{col}-{cloud_type}"] = (df[col] == cloud_type).astype(int)
        df = df.drop(columns=[col])

    wind_columns = [col for col in df.columns if 'Ветер' in col and '(м/с)' not in col]
    for col in wind_columns:
        try:
            df[col] = df[col].astype(str)
            
            df[f"{col} (м/с)"] = df[col].apply(
                lambda x: float(x.split()[-1].replace('м/с', '')) 
                if isinstance(x, str) and 'м/с' in x 
                else 0
            )
            
            directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
            for direction in directions:
                df[f"{col}-{direction}"] = (
                    df[col].str.split().str[0].fillna('').eq(direction)
                ).astype(int)
            
            df = df.drop(columns=[col])
            
        except Exception as e:
            print(f"Ошибка при обработке столбца {col}: {str(e)}")
            continue

    temp_columns = [col for col in df.columns if 'Температура' in col]
    for col in temp_columns:
        df[col] = df[col].replace({'+': '', '−': '-', 'Неизвестно': '0'}, regex=True).astype(float)

    pressure_columns = [col for col in df.columns if 'Давление' in col]
    for col in pressure_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df = df.fillna(0)
    
    return df