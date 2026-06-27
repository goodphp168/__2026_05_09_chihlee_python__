import pandas as pd

input_path = r'C:\Users\eric\Downloads\電話表.xlsx'
output_path = r'C:\Users\eric\Downloads\電話表.csv'

df = pd.read_excel(input_path)
df.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f'轉檔完成：{output_path}')
