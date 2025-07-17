Taiwan Power Data Fetcher

抓取台灣電力公司每日更新的發電數據，並儲存為 CSV 格式，後續可進行資料分析與視覺化。

 📌 功能特色

* 自動從台電官網抓取發電機組資料
* 每 60 秒檢查是否有新資料，若有更新則儲存
* 支援解析 HTML、處理註解與數值欄位
* 資料轉換為 `pandas.DataFrame`，並儲存為 CSV
* 可整合 GUI，進行資料視覺化

---

 📦 安裝需求

```bash
pip install requests pandas beautifulsoup4
```

Python 版本：`>= 3.7`

---

 📁 專案結構

```
.
├── taiwan_power.py         # 主程式，責辦資料抓取與清潔
├── data/                   # 儲存的 CSV 檔案（由使用者自行建立）
├── gui_app.py              # ( 選用 ) GUI 可視化應用
├── README.md
```

---

 🚀 如何使用

✅ CLI 模式（自動抓取）

```bash
python taiwan_power.py
```

每 60 秒會自動抓取一次，若資料有更新，將儲存為：

```
power_usage_data_202507171015.csv
```

---

 📊 欄位說明

| 欄位名稱                        | 說明                |
| --------------------------- | ----------------- |
| update\_time                | 資料更新時間            |
| energy\_type                | 能源類別（如：燃煤、核能）     |
| unit\_type                  | 機組類別（如：抽蓄、水力）     |
| unit\_name                  | 機組名稱              |
| installed\_capacity         | 裝置容量（MW）          |
| net\_generation             | 淨發電量（MW）          |
| generation\_capacity\_ratio | 淨發電 / 裝置容量 比例 (%) |
| note                        | 備註                |
| installed\_capacity\_ratio  | 裝置容量註解 (%)        |
| net\_generation\_ratio      | 淨發電註解 (%)         |

---

 🖼️ 延伸應用

* ✅ 支援整合 `tkinter` GUI 篩選日期、能源類別
* ✅ 可繪製發電量折線圖、長條圖
* 📁 支援讀取多筆 CSV（建議使用 `glob`）

---

 🛠️ Todo / 改進方向

* [ ] 將爬蟲封裝成 API Server
* [ ] 支援 SQLite / Parquet 輸出
* [ ] Web-based Dashboard（例如 Dash / Streamlit）
* [ ] 單元測試 / logging 機制強化

---

 📄 License

MIT License

---

 🤛🏻 作者

[seeker.chiou](https://github.com/seeker.chiou)
