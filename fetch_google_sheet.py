import pandas as pd
import json
import sys
import traceback

# Посилання на ваші таблиці
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
        # 1. ОБРОБКА ОСНОВНИХ ДАНИХ
        print("Завантаження основних даних...")
        df = pd.read_csv(MAIN_SHEET_URL)
        df = df.fillna(0) # Заміна NaN на 0
        
        gradients = ['linear-gradient(135deg, #FF6B6B 0%, #EE5253 100%)', 'linear-gradient(135deg, #4834d4 0%, #686de0 100%)', 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)']
        sales_data = []
        
        for _, row in df.iterrows():
            name = str(row.iloc[0])
            if name.lower() in ['nan', '0', 'разом', 'сума', 'итог']: continue
            
            metrics = {}
            for col in df.columns[2:]:
                val = clean_number(row[col])
                unit = '%' if col in PERCENT_COLUMNS else 'грн'
                metrics[col] = {'value': val, 'label': col, 'unit': unit}
            
            sales_data.append({
                'id': len(sales_data) + 1,
                'name': name,
                'position': str(row.iloc[1]),
                'initials': "".join([p[0] for p in name.split()[:2]]).upper() if len(name) > 2 else "??",
                'gradient': gradients[len(sales_data) % len(gradients)],
                'metrics': metrics
            })

        with open('sales-data.json', 'w', encoding='utf-8') as f:
            json.dump(sales_data, f, ensure_ascii=False, indent=2)
        print("✓ sales-data.json створено")

        # 2. ОБРОБКА ЩОДЕННИХ ПРОДАЖІВ
        print("Завантаження щоденних продажів...")
        df_daily = pd.read_csv(DAILY_SALES_URL)
        df_daily.columns = [c.strip() for c in df_daily.columns]
        
        # ✅ ЗАМІНА NaN НА 0 (ВИПРАВЛЯЄ ПОМИЛКУ Unexpected token N)
        df_daily = df_daily.fillna(0)
        
        daily_list = df_daily.to_dict(orient='records')
        
        with open('daily-sales.json', 'w', encoding='utf-8') as f:
            json.dump(daily_list, f, ensure_ascii=False, indent=2)
        print(f"✓ daily-sales.json створено ({len(daily_list)} рядків)")

    except Exception as e:
        print(f"ПОМИЛКА: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    process_data()
