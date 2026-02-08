import pandas as pd
import json
import sys
import traceback

MAIN_SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRxPqHp5lwwhjdDTaJdiwWYbhqZmeALG5dVhSZ6rHx2W8KGrcNWaa5-7qiVB87KKbQEXjtF1WVwmBzp/pub?gid=50416606&single=true&output=csv"
DAILY_SALES_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQOxz-ozH9yNLW3IAzlkMlbRqOTrR4sIUO1__KpAMBFEvvpMXr4LWTnRvzYGb_y6za7WBxOUhl2DV84/pub?output=csv"

PERCENT_COLUMNS = ['% Доля ACC', 'Доля Послуг', 'Конверсія ПК', 'Конверсія ПК Offline', 'Доля УДС']

def clean_number(value):
    if pd.isna(value): return 0.0
    str_val = str(value).strip().replace(' ', '').replace('\xa0', '')
    if not str_val or str_val.lower() in ['nan', 'none']: return 0.0
    if '%' in str_val:
        str_val = str_val.replace('%', '').replace(',', '.')
        try: return float(str_val)
        except: return 0.0
    if ',' in str_val and '.' in str_val:
        if str_val.find('.') < str_val.find(','):
            str_val = str_val.replace('.', '').replace(',', '.')
        else:
            str_val = str_val.replace(',', '')
    else:
        str_val = str_val.replace(',', '.')
    try: return float(str_val)
    except: return 0.0

def process_data():
    try:
        # 1. Основні дані
        df = pd.read_csv(MAIN_SHEET_URL)
        df = df.fillna(0)
        
        gradients = ['linear-gradient(135deg, #FF6B6B 0%, #EE5253 100%)', 'linear-gradient(135deg, #4834d4 0%, #686de0 100%)', 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)', 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)']
        sales_data = []
        
        for i, row in df.iterrows():
            name = str(row.iloc[0]).strip()
            # Пропускаємо тільки технічні рядки
            if not name or name.lower() in ['nan', '0', 'разом', 'сума', 'итог']: continue
            
            metrics = {}
            for col in df.columns[2:]:
                val = clean_number(row[col])
                unit = '%' if col in PERCENT_COLUMNS else 'грн'
                metrics[col] = {'value': val, 'label': col, 'unit': unit}
            
            sales_data.append({
                'id': len(sales_data) + 1,
                'name': name,
                'position': str(row.iloc[1]),
                'initials': "".join([p[0] for p in name.split()[:2]]).upper(),
                'gradient': gradients[len(sales_data) % len(gradients)],
                'metrics': metrics
            })

        # Розрахунок загальних показників (МАГ)
        store_totals = {
            'id': 0, 'name': 'Показники магазину', 'position': 'Всі продавці',
            'initials': 'ALL', 'gradient': 'linear-gradient(135deg, #434343 0%, #000000 100%)',
            'metrics': {}
        }
        for col in df.columns[2:]:
            vals = [p['metrics'][col]['value'] for p in sales_data]
            if col in PERCENT_COLUMNS:
                res = round(sum(vals)/len(vals), 2) if vals else 0
                store_totals['metrics'][col] = {'value': res, 'label': col, 'unit': '%'}
            else:
                res = round(sum(vals), 2)
                store_totals['metrics'][col] = {'value': res, 'label': col, 'unit': 'грн'}

        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump([store_totals] + sales_data, f, ensure_ascii=False, indent=2)

        # 2. Щоденні продажі
        df_daily = pd.read_csv(DAILY_SALES_URL).fillna(0)
        df_daily.columns = [c.strip() for c in df_daily.columns]
        with open('daily-sales.json', 'w', encoding='utf-8') as f:
            json.dump(df_daily.to_dict(orient='records'), f, ensure_ascii=False, indent=2)
        print("✓ Дані успішно оновлені")

    except Exception as e:
        print(f"Помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    process_data()
