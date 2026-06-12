from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import pandas as pd
import requests
from pandas import DataFrame
from requests import Response

from report import export_to_pdf


# 台北市 YouBike 2.0 的 Web API 網址
YOUBIKE_URL = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"


class YouBikeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("YouBike 即時資料查詢")
        self.root.geometry("980x620")

        self.df: DataFrame | None = None

        self.status_var = tk.StringVar(value="請先點選『下載資料』")
        self.count_var = tk.StringVar(value="目前資料筆數：0")

        self._build_ui()

    def _build_ui(self) -> None:
        top_frame = ttk.Frame(self.root, padding=12)
        top_frame.pack(fill="x")

        download_button = ttk.Button(top_frame, text="下載資料", command=self.download_data)
        download_button.pack(side="left")

        export_button = ttk.Button(top_frame, text="匯出 PDF", command=self.export_pdf)
        export_button.pack(side="left", padx=8)

        ttk.Label(top_frame, textvariable=self.count_var).pack(side="left", padx=12)

        status_frame = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        status_frame.pack(fill="x")
        ttk.Label(status_frame, textvariable=self.status_var, foreground="#1f4e79").pack(anchor="w")

        table_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        table_frame.pack(fill="both", expand=True)

        columns = ("sna", "sarea", "ar", "tot", "sbi", "bemp", "mday")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        headings = {
            "sna": "站點名稱",
            "sarea": "行政區",
            "ar": "地址",
            "tot": "總車位",
            "sbi": "可借",
            "bemp": "可還",
            "mday": "更新時間",
        }

        widths = {
            "sna": 180,
            "sarea": 90,
            "ar": 260,
            "tot": 70,
            "sbi": 70,
            "bemp": 70,
            "mday": 170,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

    def download_data(self) -> None:
        self.status_var.set("資料下載中，請稍候...")
        self.root.update_idletasks()

        try:
            response: Response = requests.get(YOUBIKE_URL, timeout=15)
            response.raise_for_status()
            data: list[dict] = response.json()
            self.df = pd.DataFrame(data=data)
        except requests.RequestException as exc:
            self.status_var.set("下載失敗")
            messagebox.showerror("下載失敗", f"無法取得資料：{exc}")
            return

        self.count_var.set(f"目前資料筆數：{len(self.df)}")
        self.status_var.set("下載完成，已更新表格預覽")
        self._refresh_table()

    def _normalize_columns(self, df: DataFrame) -> DataFrame:
        # 兼容新舊 YouBike API 欄位名稱
        alias_candidates = {
            "tot": ["tot", "total"],
            "sbi": ["sbi", "available_rent_bikes"],
            "bemp": ["bemp", "available_return_bikes"],
        }

        for target, candidates in alias_candidates.items():
            if target in df.columns:
                continue

            matched = next((col for col in candidates if col in df.columns), None)
            if matched is not None:
                df[target] = df[matched]

        return df

    def _refresh_table(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        if self.df is None:
            return

        preview_columns = ["sna", "sarea", "ar", "tot", "sbi", "bemp", "mday"]
        normalized_df = self._normalize_columns(self.df.copy())
        if not any(col in normalized_df.columns for col in preview_columns):
            self.status_var.set("找不到可預覽的欄位")
            return

        table_df = normalized_df.reindex(columns=preview_columns, fill_value="")

        for _, row in table_df.fillna("").head(200).iterrows():
            self.tree.insert("", "end", values=tuple(row.astype(str)))

    def export_pdf(self) -> None:
        if self.df is None or self.df.empty:
            messagebox.showwarning("尚無資料", "請先下載資料再匯出 PDF。")
            return

        output_file = Path(__file__).with_name("youbike_report.pdf")
        export_to_pdf(self._normalize_columns(self.df.copy()), output_file)
        self.status_var.set(f"已匯出 PDF：{output_file.name}")
        messagebox.showinfo("匯出完成", f"PDF 已產生：\n{output_file}")


def main() -> None:
    root = tk.Tk()
    app = YouBikeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
