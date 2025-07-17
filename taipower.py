import requests
import pandas as pd
from decimal import Decimal
from bs4 import BeautifulSoup
import time


class TaiwanPowerFetcher:
    def __init__(self):
        self.url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/genary.json"
        self.last_fetch_time = None

    def fetch_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Fetch failed: {e}")
            return None

    def clean_data(self, raw_json):
        # clean logic
        return

    def to_dataframe(self, data):
        return pd.DataFrame(data)

    def parse_html_text(self, html):
        """從 HTML 中取出純文字，例如 <b>xxx</b>"""
        return BeautifulSoup(html, "html.parser").get_text(strip=True)
        # convert to pd.DataFrame

    def extract_update_time(self, raw_json):
        return raw_json.get("", "")

    def extract_value_and_note(self, text):
        """從 '123(註解)' 格式中抽出數值與註解"""
        note = ""
        if "(" in text and ")" in text:
            note = text[text.find("(")+1: text.find(")")]
            text = text[:text.find("(")]

        if "%" in note:
            note = note.replace("%", "")

        return text.strip(), note

    def extract_power_usage(self, raw_json):
        data = raw_json.get('aaData', [])
        result = []
        for item in data:
            # 取出純文字
            energy_type = self.parse_html_text(item[0])
            unit_type = self.parse_html_text(item[1])
            unit_name = self.parse_html_text(item[2])

            # 處理數值與註解
            installed_capacity, note1 = self.extract_value_and_note(item[3])
            net_generation, note2 = self.extract_value_and_note(item[4])

            # 將數值轉為 Decimal
            if installed_capacity[0].isdigit():
                installed_capacity = Decimal(installed_capacity)
            else:
                installed_capacity = Decimal(0)

            if net_generation[0].isdigit():
                net_generation = Decimal(net_generation)
            else:
                net_generation = Decimal(0)

            generation_capacity_ratio = item[5]
            note = item[6]

            # 添加註解
            result.append({
                "energy_type": energy_type,
                "unit_type": unit_type,
                "unit_name": unit_name,
                "installed_capacity": installed_capacity,
                "net_generation": net_generation,
                "generation_capacity_ratio": generation_capacity_ratio,
                "note": note,
                "installed_capacity_ratio": note1,
                "net_generation_ratio": note2
            })

        return result

    def has_data_updated(self, current_time):
        if self.last_fetch_time != current_time:
            self.last_fetch_time = current_time
            return True
        return False


if __name__ == "__main__":
    tp = TaiwanPowerFetcher()

    while True:
        raw = tp.fetch_data()

        if not raw:
            print("No data fetched.")
            time.sleep(60)
            continue
            # exit()

        current_date = tp.extract_update_time(raw)

        if tp.has_data_updated(current_date):
            clean = tp.extract_power_usage(raw)

            df = pd.DataFrame(clean)
            df.insert(0, 'update_time', current_date)
            filename = f'data/power_usage_data_{current_date.replace(" ", "").replace("-", "").replace(":", "")}.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[INFO] Data saved to {filename}")

        time.sleep(60)  # 每60秒檢查一次
