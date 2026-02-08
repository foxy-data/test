import pandas as pd
import json
import sys
import traceback

# Константи
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

    # Обробка роздільників тисяч та десяткових
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
        # --- ЧАСТИНА 1: Основні показники команди ---
        print("Завантаження основних даних...")
        df = pd.read_csv(MAIN_SHEET_URL)
        
        gradients = [
            'linear-gradient(135deg, #FF6B6B 0%, #EE5253 100%)',
            'linear-gradient(135deg, #4834d4 0%, #686de0 100%)',
            'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)',
            'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'linear-gradient(135deg, #fa709a 0%, #fee140 100%)'
        ]

        sales_data = []
        for _, row in df.iterrows():
            name = str(row.iloc[0])
            position = str(row.iloc[1])
            if name.lower() in ['nan', 'разом', 'итог', 'сума']: continue

            parts = name.split()
            initials = "".join([p[0] for p in parts[:2]]).upper() if len(parts) >= 2 else name[:2].upper()

            metrics = {}
            for col in df.columns[2:]:
                val = clean_number(row[col])
                unit = ''
                if col in PERCENT_COLUMNS: unit = '%'
                elif col in ['Шт.', 'Чеки', 'ПЧ']: unit = 'шт'
                else: unit = 'грн'
                
                metrics[col] = {'value': val, 'label': col, 'unit': unit}

            sales_data.append({
                'id': len(sales_data) + 1,
                'name': name,
                'position': position,
                'initials': initials,
                'gradient': gradients[len(sales_data) % len(gradients)],
                'metrics': metrics
            })

        # Загальні показники
        store_totals = {
            'id': 0, 'name': 'Загальні показники магазину', 'position': 'Всі продавці',
            'initials': 'МАГ', 'gradient': 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
            'metrics': {}
        }
        for col in df.columns[2:]:
            values = [p['metrics'][col]['value'] for p in sales_data]
            if col in PERCENT_COLUMNS:
                avg = round(sum(values) / len(values), 2) if values else 0
                store_totals['metrics'][col] = {'value': avg, 'label': col, 'unit': '%'}
            elif col in ['Шт.', 'Чеки', 'ПЧ']:
                store_totals['metrics'][col] = {'value': int(sum(values)), 'label': col, 'unit': 'шт'}
            else:
                store_totals['metrics'][col] = {'value': round(sum(values), 2), 'label': col, 'unit': 'грн'}

        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump([store_totals] + sales_data, f, ensure_ascii=False, indent=2)
        print("✓ sales-data.json оновлено")

        # --- ЧАСТИНА 2: Щоденні продажі ---
        print("Завантаження щоденних продажів...")
        df_daily = pd.read_csv(DAILY_SALES_URL)
        df_daily.columns = [c.strip() for c in df_daily.columns]
        daily_list = df_daily.to_dict(orient='records')
        
        with open('daily-sales.json', 'w', encoding='utf-8') as f:
            json.dump(daily_list, f, ensure_ascii=False, indent=2)
        print(f"✓ daily-sales.json оновлено ({len(daily_list)} рядків)")

    except Exception as e:
        print(f"ПОМИЛКА: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    process_data()
