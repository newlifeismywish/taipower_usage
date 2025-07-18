import tkinter as tk
from tkinter import ttk
import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
plt.rcParams["font.family"] = "Microsoft JhengHei"


def load_all_csv_data(folder="data"):
    files = glob.glob(os.path.join(folder, "*.csv"))
    all_data = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    all_data["update_time"] = pd.to_datetime(all_data["update_time"])
    return all_data


def plot_chart(df, metric, energy_type, unit_type, unit_name, start_date, end_date, user_period="10min"):
    filtered = df.copy()

    # 時間範圍過濾
    try:
        if start_date != "全部":
            start = pd.to_datetime(start_date)
            filtered = filtered[filtered["update_time"] >= start]
        if end_date != "全部":
            end = pd.to_datetime(end_date)
            filtered = filtered[filtered["update_time"] <= end]
    except Exception:
        pass  # 解析失敗就不過濾

    # 其他條件過濾
    if energy_type != "全部":
        filtered = filtered[filtered["energy_type"] == energy_type]
    if unit_type != "全部":
        filtered = filtered[filtered["unit_type"] == unit_type]
    if unit_name != "全部":
        filtered = filtered[filtered["unit_name"] == unit_name]
    else:
        filtered = filtered[filtered["unit_name"] != "小計"]

    filtered["time_group"] = filtered["update_time"].dt.floor(user_period)

    # 分組並求和（或平均，看需求）
    # grouped = filtered.groupby("time_group")[metric].sum()
    grouped = filtered.groupby(["time_group", "energy_type"])[
        metric].sum().unstack()

    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.plot(ax=ax, marker="o")
    ax.set_title(f"{metric} over Time")
    ax.set_xlabel("Update Time")
    ax.set_ylabel(metric)
    ax.grid(True)
    plt.legend(title="類別", loc='center left', bbox_to_anchor=(1.0, 0.5))
    plt.tight_layout()
    return fig


class PowerUsageGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Taiwan Power Usage Viewer")
        self.geometry("1400x900")

        self.data = load_all_csv_data()

        # 把所有欄位的選項放好，排除NaN、加"全部"
        self.energy_types = ["全部"] + \
            sorted(self.data["energy_type"].dropna().unique())
        self.unit_types = ["全部"] + \
            sorted(self.data["unit_type"].dropna().unique())
        self.unit_names = ["全部"] + \
            sorted(self.data["unit_name"].dropna().unique())
        self.metric_types = ["installed_capacity", "net_generation", "generation_capacity_ratio",
                             "installed_capacity_ratio", "net_generation_ratio"]

        # 建立日期範圍選單，抓取資料時間範圍並製作選項
        self.date_ranges = self.generate_date_ranges()

        self.create_widgets()
        self.bind_events()

    def generate_date_ranges(self):
        dates = self.data["update_time"].dropna().sort_values().unique()
        if len(dates) == 0:
            return ["全部"]

        start = dates.min()
        end = dates.max()
        full_range = f"{start.date()} ~ {end.date()}"

        # 你可以在這裡加更多自訂日期區間選項
        return ["全部"]+dates.tolist()

    def create_widgets(self):
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10, padx=10, fill=tk.X)

        # 日期範圍
        tk.Label(control_frame, text="起始時間:").grid(
            row=1, column=0, sticky="w", padx=5)
        self.combo_start_date = ttk.Combobox(
            control_frame, values=self.date_ranges, width=25)
        self.combo_start_date.set(self.date_ranges[0])
        self.combo_start_date.grid(row=1, column=1, padx=5)

        tk.Label(control_frame, text="  結束時間:").grid(
            row=1, column=2, sticky="w", padx=5)

        self.combo_end_date = ttk.Combobox(
            control_frame, values=self.date_ranges, width=25)
        self.combo_end_date.set(self.date_ranges[0])
        self.combo_end_date.grid(row=1, column=3, padx=5)

        # 能源類別
        tk.Label(control_frame, text="能源類別:").grid(
            row=0, column=0, sticky="w", padx=5)
        self.combo_energy = ttk.Combobox(
            control_frame, values=self.energy_types, width=15)
        self.combo_energy.set(self.energy_types[0])
        self.combo_energy.grid(row=0, column=1, padx=5)

        # 機組類別
        tk.Label(control_frame, text="機組類別:").grid(
            row=0, column=2, sticky="w", padx=5)
        self.combo_unit = ttk.Combobox(
            control_frame, values=self.unit_types, width=15)
        self.combo_unit.set(self.unit_types[0])
        self.combo_unit.grid(row=0, column=3, padx=5)

        # 機組名稱
        tk.Label(control_frame, text="機組名稱:").grid(
            row=0, column=4, sticky="w", padx=5)
        self.combo_unit_name = ttk.Combobox(
            control_frame, values=self.unit_names, width=20)
        self.combo_unit_name.set(self.unit_names[0])
        self.combo_unit_name.grid(row=0, column=5, padx=5)

        # 指標
        tk.Label(control_frame, text="指標:").grid(
            row=0, column=6, sticky="w", padx=5)
        self.combo_metric = ttk.Combobox(
            control_frame, values=self.metric_types, width=15)
        self.combo_metric.set(self.metric_types[1])
        self.combo_metric.grid(row=0, column=7, padx=5)

        # 繪圖按鈕
        self.plot_button = tk.Button(
            control_frame, text="繪圖", command=self.draw_plot)
        self.plot_button.grid(row=1, column=4, padx=10)

        # 圖表顯示區
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

    def bind_events(self):
        self.combo_energy.bind("<<ComboboxSelected>>", self.on_energy_selected)
        self.combo_unit.bind("<<ComboboxSelected>>", self.on_unit_selected)
        # self.combo_end_date.bind(
        #     "<<ComboboxSelected>>", self.on_end_date_selected)
        # self.combo_start_date.bind(
        #     "<<ComboboxSelected>>", self.on_start_date_selected)

    def on_energy_selected(self, event=None):
        selected_energy = self.combo_energy.get()
        if selected_energy == "全部":
            subset = self.data
        else:
            subset = self.data[self.data["energy_type"] == selected_energy]

        unit_types = subset["unit_type"].dropna().unique()
        unit_types = ["全部"] + sorted(unit_types.tolist())

        self.combo_unit["values"] = unit_types
        self.combo_unit.set(unit_types[0])

        # 同步更新 unit_name
        self.on_unit_selected()

    def on_unit_selected(self, event=None):
        selected_energy = self.combo_energy.get()
        selected_unit = self.combo_unit.get()

        subset = self.data
        if selected_energy != "全部":
            subset = subset[subset["energy_type"] == selected_energy]
        if selected_unit != "全部":
            subset = subset[subset["unit_type"] == selected_unit]

        unit_names = subset["unit_name"].dropna().unique()
        unit_names = ["全部"] + sorted(unit_names.tolist())

        self.combo_unit_name["values"] = unit_names
        self.combo_unit_name.set(unit_names[0])

    def on_start_date_selected(self, event=None):
        selected_start_date = self.combo_start_date.get()
        selected_end_date = self.combo_end_date.get()
        if selected_start_date == "全部":
            return

        # 更新結束日期選項
        start_date = pd.to_datetime(selected_start_date)

        if selected_end_date == "全部":
            end_dates = self.data[self.data["update_time"] >=
                                  start_date]["update_time"].dropna().unique()
        else:
            end_date = pd.to_datetime(selected_end_date)
            end_dates = self.data[(self.data["update_time"] >= start_date) & (
                self.data["update_time"] <= end_date)]["update_time"].dropna().unique()

        end_dates = ["全部"] + sorted(end_dates.tolist())

        self.combo_end_date["values"] = end_dates
        self.combo_end_date.set(selected_end_date)

    def on_end_date_selected(self, event=None):
        selected_start_date = self.combo_start_date.get()
        selected_end_date = self.combo_end_date.get()
        if selected_end_date == "全部":
            return

        # 更新開始日期選項
        end_date = pd.to_datetime(selected_end_date)

        if selected_start_date == "全部":
            start_dates = self.data[self.data["update_time"]
                                    <= end_date]["update_time"].dropna().unique()
        else:
            start_date = pd.to_datetime(selected_start_date)
            start_dates = self.data[(self.data["update_time"] >= start_date) & (
                self.data["update_time"] <= end_date)]["update_time"].dropna().unique()

        start_dates = ["全部"] + sorted(start_dates.tolist())
        self.combo_start_date["values"] = start_dates
        self.combo_start_date.set(selected_start_date)

    def draw_plot(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        selected_start_date = self.combo_start_date.get()
        selected_end_date = self.combo_end_date.get()
        selected_energy = self.combo_energy.get()
        selected_unit = self.combo_unit.get()
        selected_unit_name = self.combo_unit_name.get()
        selected_metric = self.combo_metric.get()

        fig = plot_chart(
            self.data,
            metric=selected_metric,
            energy_type=selected_energy,
            unit_type=selected_unit,
            unit_name=selected_unit_name,
            start_date=selected_start_date,
            end_date=selected_end_date
        )

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = PowerUsageGUI()
    app.mainloop()
