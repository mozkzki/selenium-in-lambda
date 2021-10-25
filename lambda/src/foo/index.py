import os
import sys
import traceback

import moz_image as image
from chronyk import Chronyk
from selenium.webdriver import Chrome, ChromeOptions


def check_env(key: str, is_check: bool = True) -> str:
    value = os.environ.get(key, "")
    if is_check:
        if not value:
            print(f"Not found environment variable: ({key} = {value})")
            sys.exit(1)
    print(f"env | {key}: {value}")
    return value


def create_driver():
    options = ChromeOptions()
    options.binary_location = os.environ.get("CHROME_BINARY_LOCATION")

    # 基本
    options.add_argument("--headless")  # local(Mac)でUI表示して確認する場合はコメントアウト
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")  # local(Mac)でUI表示して確認する場合はコメントアウト
    # ログ関連
    options.add_argument("--enable-logging")
    options.add_argument("--v=99")
    # その他
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-desktop-notifications")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-application-cache")
    options.add_argument("--start-maximized")
    options.add_argument("--no-zygote")
    options.add_argument("--hide-scrollbars")
    options.add_argument("--dns-prefetch-disable")
    options.add_argument("--user-data-dir=/tmp/chrome-user-data")
    options.add_argument("--lang=ja")
    # UA
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"  # noqa E501
    options.add_argument("--user-agent=" + user_agent)

    # options.add_argument('--window-size=1280x1696')
    # options.add_argument('--log-level=0')
    # options.add_argument('--remote-debugging-port=9222')
    # options.add_argument("--disable-setuid-sandbox")
    # options.page_load_strategy = 'none'

    driver = Chrome(options=options, executable_path=os.environ.get("CHROME_DRIVER_LOCATION"))
    driver.set_window_size(1280, 720)
    driver.set_page_load_timeout(30)

    return driver


def handler(event, context):
    task_root = check_env("LAMBDA_TASK_ROOT", is_check=False)
    home = check_env("HOME", is_check=False)
    check_env("CHROME_BINARY_LOCATION")
    check_env("CHROME_DRIVER_LOCATION")
    check_env("gyazo_access_token")

    os.system(f"ls -al {task_root}")
    os.system(f"ls -al {home}")

    test = Chronyk("now").ctime()
    print(f"lib load test: Chronyk('now').ctime()={test}")

    # Chromedriver生成
    driver = create_driver()

    # ページ遷移(Yahoo天気へ)
    try:
        # 何故かYahoo天気のページはgetがtimeoutする(他のページは正常)
        # timeoutしても遷移&screenshot撮影は成功するので例外補足して進む
        driver.get("https://weather.yahoo.co.jp/weather/jp/13/4410.html")
    except Exception:
        traceback.print_exc()

    # screenshot撮影、GYAZOにアップロード
    TMP_OUTPUT_FILE = "/tmp/screenshot_tmp.png"
    driver.get_screenshot_as_file(TMP_OUTPUT_FILE)
    screenshot_url = image.upload_to_gyazo(TMP_OUTPUT_FILE)

    # Chromedriver破棄
    driver.quit()

    return {"statusCode": 200, "body": f"success upload screenshot: {screenshot_url}"}
