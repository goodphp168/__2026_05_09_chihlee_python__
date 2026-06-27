import csv
import tempfile
import unittest
from pathlib import Path

import read


class TableCleanupTest(unittest.TestCase):
    def test_clean_table_trims_cells_and_removes_duplicate_rows(self):
        rows = [
            [" 職掌名稱 ", "Unnamed: 1", " 分機號碼 "],
            [" 校長室 ", " 邱炳坤校長 1608 ", ""],
            [" 校長室 ", " 邱炳坤校長 1608 ", ""],
            ["", "", ""],
        ]

        cleaned = read.clean_table(rows)

        self.assertEqual(
            cleaned,
            [
                ["職掌名稱", "Unnamed: 1", "分機號碼"],
                ["校長室", "邱炳坤校長 1608", ""],
            ],
        )

    def test_save_csv_writes_utf8_sig_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "整理後.csv"

            read.save_csv(output_path, [["欄位"], ["內容"]])

            with output_path.open("r", encoding="utf-8-sig", newline="") as file:
                self.assertEqual(list(csv.reader(file)), [["欄位"], ["內容"]])

    def test_make_vertical_table_keeps_non_empty_cells(self):
        rows = [
            ["職掌名稱", "Unnamed: 1", "分機號碼"],
            ["校長室", "邱炳坤校長 1608", ""],
        ]

        vertical_rows = read.make_vertical_table(rows)

        self.assertEqual(
            vertical_rows,
            [
                ["原始列", "原始欄", "內容"],
                ["2", "職掌名稱", "校長室"],
                ["2", "Unnamed: 1", "邱炳坤校長 1608"],
            ],
        )

    def test_search_records_finds_keyword_in_content(self):
        records = [
            {"原始列": "2", "原始欄": "職掌名稱", "內容": "校長室"},
            {"原始列": "2", "原始欄": "Unnamed: 1", "內容": "邱炳坤校長 1608"},
        ]

        results = read.search_records(records, "1608")

        self.assertEqual(results, [records[1]])

    def test_search_records_is_case_insensitive_and_ignores_spaces(self):
        records = [
            {"原始列": "8", "原始欄": "Unnamed: 19", "內容": "王俊杰 活動組組長 8102"},
        ]

        results = read.search_records(records, " 王俊杰 ")

        self.assertEqual(results, records)

    def test_format_search_results_returns_professional_table(self):
        records = [
            {"原始列": "2", "原始欄": "Unnamed: 1", "內容": "邱炳坤校長 1608"},
        ]

        table = read.format_search_results(records)

        self.assertIn("原始列", table)
        self.assertIn("原始欄", table)
        self.assertIn("內容", table)
        self.assertIn("邱炳坤校長 1608", table)

    def test_build_query_report_shows_count_and_no_result_message(self):
        records = [
            {"原始列": "2", "原始欄": "Unnamed: 1", "內容": "邱炳坤校長 1608"},
        ]

        matched_report = read.build_query_report("1608", records)
        empty_report = read.build_query_report("9999", [])

        self.assertIn("分機查詢系統", matched_report)
        self.assertIn("共 1 筆", matched_report)
        self.assertIn("查詢關鍵字：1608", matched_report)
        self.assertIn("查無符合資料。", empty_report)


if __name__ == "__main__":
    unittest.main()
