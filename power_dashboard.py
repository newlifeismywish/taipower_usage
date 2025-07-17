import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PowerUsageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("台灣電力資料視覺化")

        # 載入資料
        self.df = pd.read_csv("power_usage_data_202507171320.csv")  # 或合併多日的資料

        # 取得可選條件
        self.dates = sorted(self.df['update_time'].unique(
        )) if 'update_time' in self.df.columns else ['2025-07-17']
        self.energy_types = sorted(self.df['energy_type'].unique())

        # 建立介面
        self.create_widgets()

    def create_widgets(self):
        # 日期選單
        ttk.Label(self.root, text="選擇日期:").grid(row=0, column=0)
        self.date_cb = ttk.Combobox(self.root, values=self.dates)
        self.date_cb.grid(row=0, column=1)

        # 能源類型選單
        ttk.Label(self.root, text="選擇能源類別:").grid(row=1, column=0)
        self.energy_cb = ttk.Combobox(self.root, values=self.energy_types)
        self.energy_cb.grid(row=1, column=1)

        # 顯示按鈕
        self.btn = ttk.Button(self.root, text="顯示圖表", command=self.show_chart)
        self.btn.grid(row=2, column=0, columnspan=2, pady=10)

        # 畫布
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2)

    def show_chart(self):
        date = self.date_cb.get()
        energy = self.energy_cb.get()

        if not date or not energy:
            return

        # 過濾資料
        df_filtered = self.df[
            (self.df['update_time'] == date) &
            (self.df['energy_type'] == energy)
        ]

        if df_filtered.empty:
            self.ax.clear()
            self.ax.set_title("無資料")
            self.canvas.draw()
            return

        # 畫圖
        self.ax.clear()
        self.ax.plot(df_filtered['unit_name'],
                     df_filtered['net_generation'], marker='o')
        self.ax.set_title(f"{date} {energy} 淨發電量")
        self.ax.set_xlabel("機組名稱")
        self.ax.set_ylabel("淨發電量 (MW)")
        self.ax.tick_params(axis='x', rotation=45)
        self.canvas.draw()


# 啟動 GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = PowerUsageApp(root)
    root.mainloop()
