import pdfplumber
import pandas as pd
import os

pdf_path = r'C:\Users\eric\Downloads\電話表.pdf'
output_path = r'C:\Users\eric\Downloads\電話表.xlsx'

with pdfplumber.open(pdf_path) as pdf:
    all_rows = []
    headers = None
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if not table:
                continue
            if headers is None:
                headers = table[0]
                all_rows.extend(table[1:])
            else:
                all_rows.extend(table[1:])

if headers and all_rows:
    df = pd.DataFrame(all_rows, columns=headers)
    df.to_excel(output_path, index=False)
    print(f'轉檔完成：{output_path}')
else:
    print('未偵測到表格資料')

