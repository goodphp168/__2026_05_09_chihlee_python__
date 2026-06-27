import csv
import re
import sys
from pathlib import Path


SOURCE_CSV = Path(r"C:\Users\eric\Downloads\電話表.csv")
OUTPUT_CSV = Path(__file__).with_name("整理後_電話表.csv")
VERTICAL_OUTPUT_CSV = Path(__file__).with_name("整理後_電話表_直式.csv")
SEARCH_COLUMNS = ["原始列", "原始欄", "內容"]


def clean_cell(value):
    return re.sub(r"\s+", " ", value).strip()


def load_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.reader(file))


def clean_table(rows):
    cleaned_rows = []
    seen = set()

    for row in rows:
        cleaned_row = [clean_cell(cell) for cell in row]

        if not any(cleaned_row):
            continue

        row_key = tuple(cleaned_row)
        if row_key in seen:
            continue

        seen.add(row_key)
        cleaned_rows.append(cleaned_row)

    return cleaned_rows


def save_csv(path, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def make_vertical_table(rows):
    if not rows:
        return [SEARCH_COLUMNS]

    headers = rows[0]
    vertical_rows = [SEARCH_COLUMNS]

    for row_number, row in enumerate(rows[1:], start=2):
        for column_index, cell in enumerate(row):
            if not cell:
                continue

            header = headers[column_index] if column_index < len(headers) else f"欄位{column_index + 1}"
            vertical_rows.append([str(row_number), header, cell])

    return vertical_rows


def rows_to_records(rows):
    if not rows:
        return []

    headers = rows[0]
    records = []

    for row in rows[1:]:
        record = {}
        for index, header in enumerate(headers):
            record[header] = row[index] if index < len(row) else ""
        records.append(record)

    return records


def search_records(records, keyword):
    normalized_keyword = clean_cell(keyword).casefold()

    if not normalized_keyword:
        return records

    results = []
    for record in records:
        searchable_text = " ".join(record.get(column, "") for column in SEARCH_COLUMNS).casefold()
        if normalized_keyword in searchable_text:
            results.append(record)

    return results


def format_search_results(records):
    if not records:
        return "查無符合資料。"

    widths = {
        column: max(len(column), *(len(record.get(column, "")) for record in records))
        for column in SEARCH_COLUMNS
    }

    header = " | ".join(column.ljust(widths[column]) for column in SEARCH_COLUMNS)
    divider = "-+-".join("-" * widths[column] for column in SEARCH_COLUMNS)
    body = [
        " | ".join(record.get(column, "").ljust(widths[column]) for column in SEARCH_COLUMNS)
        for record in records
    ]

    return "\n".join([header, divider, *body])


def build_query_report(keyword, records):
    lines = [
        "=== 分機查詢系統 ===",
        f"查詢關鍵字：{keyword}",
        f"查詢結果：共 {len(records)} 筆",
        "",
        format_search_results(records),
    ]
    return "\n".join(lines)


def print_usage():
    print("=== 分機查詢系統 ===")
    print("用法：python read.py 關鍵字")
    print("範例：python read.py 1608")
    print("範例：python read.py 王俊杰")


def print_table(rows):
    for row in rows:
        print(" | ".join(row))


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    rows = load_csv(SOURCE_CSV)
    cleaned_rows = clean_table(rows)
    vertical_rows = make_vertical_table(cleaned_rows)

    save_csv(OUTPUT_CSV, cleaned_rows)
    save_csv(VERTICAL_OUTPUT_CSV, vertical_rows)

    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])
        records = rows_to_records(vertical_rows)
        results = search_records(records, keyword)
        print(build_query_report(keyword, results))
        print()
        print(f"整理資料：{OUTPUT_CSV}")
        print(f"查詢資料：{VERTICAL_OUTPUT_CSV}")
        return

    print_usage()
    print()
    print(f"已輸出：{OUTPUT_CSV}")
    print(f"已輸出：{VERTICAL_OUTPUT_CSV}")


if __name__ == "__main__":
    main()
