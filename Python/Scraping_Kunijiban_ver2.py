##完成版??　
# データのDLのみ　修正後　PCがスリープにならないように注意
"""
更新内容  11/3
１．WebDriverWait と time.sleep の調整:
time.sleep の代わりに WebDriverWait を使い、ページが読み込まれるまで待機してから処理を続行するように変更
２．並列処理: 
concurrent.futures.ThreadPoolExecutor を用いて、XMLデータのダウンロードを並列化し、複数のファイルを同時にダウンロード
３．次ページリンクのエラーハンドリング: 
次ページへの移動ができないときはループを終了するように変更
"""

"""　更新内容 11/4　
修正内容：
総ページ数 total_page_numberの追加
プログラムの挙動に問題がないことを確認
"""


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests
import re
import concurrent.futures
import time

# ダウンロードディレクトリを設定
base_download_dir = r"C:\Users\takumi\Downloads"
download_dir = os.path.join(base_download_dir, "大阪平野_ボーリングデータ")

# ダウンロードディレクトリが存在しない場合は作成
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

# Chromeのオプション設定
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# WebDriverの設定
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Kunijibanサイトにアクセス
driver.get('https://www.kunijiban.pwri.go.jp/viewer/')

# 手順2: 左の >ボタンをクリック
wait = WebDriverWait(driver, 10)
left_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="bar"]/div')))
left_button.click()

# 手順3: 詳細なボーリング検索はこちら をクリック
search_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, '詳細なボーリング検索はこちら')))
search_button.click()

# 手順4: 範囲指定の枠に緯度経度の数値を打ち込む
latitude_start = [34, 15, 0]  # 北緯開始（度,分,秒)
latitude_end = [35, 0, 0]    # 北緯終了（度,分,秒)
longitude_start = [135, 0, 0]  # 東経開始（度,分,秒)
longitude_end = [135, 52, 30]    # 東経終了（度,分,秒)

# 緯度経度を入力
lat_start_deg_field = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[1]')))
lat_start_min_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[2]')
lat_start_sec_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[3]')
lat_end_deg_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[4]')
lat_end_min_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[5]')
lat_end_sec_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[2]/input[6]')
lon_start_deg_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[1]')
lon_start_min_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[2]')
lon_start_sec_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[3]')
lon_end_deg_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[4]')
lon_end_min_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[5]')
lon_end_sec_field = driver.find_element(By.XPATH, '//*[@id="search"]/form/dl/dd[9]/div[3]/input[6]')

# フィールドに値を入力
lat_start_deg_field.clear(); lat_start_deg_field.send_keys(str(latitude_start[0]))
lat_start_min_field.clear(); lat_start_min_field.send_keys(str(latitude_start[1]))
lat_start_sec_field.clear(); lat_start_sec_field.send_keys(str(latitude_start[2]))
lat_end_deg_field.clear(); lat_end_deg_field.send_keys(str(latitude_end[0]))
lat_end_min_field.clear(); lat_end_min_field.send_keys(str(latitude_end[1]))
lat_end_sec_field.clear(); lat_end_sec_field.send_keys(str(latitude_end[2]))
lon_start_deg_field.clear(); lon_start_deg_field.send_keys(str(longitude_start[0]))
lon_start_min_field.clear(); lon_start_min_field.send_keys(str(longitude_start[1]))
lon_start_sec_field.clear(); lon_start_sec_field.send_keys(str(longitude_start[2]))
lon_end_deg_field.clear(); lon_end_deg_field.send_keys(str(longitude_end[0]))
lon_end_min_field.clear(); lon_end_min_field.send_keys(str(longitude_end[1]))
lon_end_sec_field.clear(); lon_end_sec_field.send_keys(str(longitude_end[2]))

# 詳細検索を実行ボタンをクリック
search_detail_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search"]/form/dl/dd[10]/div[1]/input[1]')))
search_detail_button.click()

# 手順5: 表示された範囲内のデータをすべてダウンロード
time.sleep(1)

# 5.1 範囲内に該当する件数を表示してDLするかどうかをユーザーに確認する
results_count = driver.find_element(By.XPATH, '//*[@id="search"]/div/div[1]/div').text


# 正規表現で「全 xxx ページ」の xxx 部分を抽出
match = re.search(r"全\s(\d+)\sページ", results_count)
if match:
    total_page_number = int(match.group(1))  # 抽出したページ数を整数に変換
    print(f"総ページ数: {total_page_number} ページ")
    
else:
    print("ページ数を抽出できませんでした。")

print(f"{results_count} が見つかりました。ダウンロードを開始しますか？ (y/n)")
user_input = input().strip().lower()

    
if user_input != 'y':
    print("ダウンロードをキャンセルしました。")
    driver.quit()

# XMLデータのダウンロード関数
def download_xml(xml_url, download_dir):
    try:
        response = requests.get(xml_url)
        filename = re.sub(r'[\\/*?:"<>|]', '_', xml_url.split('id=')[-1] + '.xml')
        filename = os.path.join(download_dir, filename)
        with open(filename, 'wb') as file:
            file.write(response.content)
        return 1
    except Exception as e:
        print(f"Error downloading {xml_url}: {e}")
        return 0

# ページごとにデータをダウンロード
page_number = 1
download_count = 0

while True:
    try:
        print(f"\nページ {page_number} のダウンロードを開始します...")
        
        # ページ内のXMLリンクを取得
        points = driver.find_elements(By.XPATH, '//a[contains(@href, "refer/?data=boring&type=xml&id=")]')

        # 並列処理でXMLデータをダウンロード
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            download_results = list(executor.map(lambda point: download_xml(point.get_attribute('href'), download_dir), points))
        page_download_count = sum(download_results)
        download_count += page_download_count

        # ページごとのダウンロード数を表示
        print(f"ページ {page_number} のダウンロード完了。ダウンロード件数: {page_download_count} 件")

        # 次のページへのリンクを取得してクリック
        page_number += 1
        next_page_xpath = f'//*[@id="search"]/div/div[1]/ul/li[{page_number}]' if page_number <= 4 else '//*[@id="search"]/div/div[1]/ul/li[6]'
        
        # 次ページのリンクを待機してクリック
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_page_xpath))).click()

        # ページ移動後、数秒待機して次のデータを取得
        time.sleep(3)  # ページ遷移のための待機時間

    except Exception as e:
        print("次のページへの移動ができないため、終了します。", e)
        break

# ブラウザを閉じる
driver.quit()
print(f"\n合計で {download_count} 件のデータをダウンロードしました。")
