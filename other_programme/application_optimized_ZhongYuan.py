import requests
from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor

def new_property_scraper():
    with sync_playwright() as p:
        # 1. 浏览器配置
        browser = p.chromium.launch(
            headless=False,  # 调试时可设为False
            channel="chrome",
            timeout=60000
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        # 2. 文件准备
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'new_properties_{timestamp}.csv'

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['成交日期', '房产名称与位置', '价格(HKD)', '面积(呎)', '单价', '中介公司', '图片链接'])

        # 3. 访问目标页面
        page.goto("https://hk.centanet.com/findproperty/zh-cn/list/transaction", timeout=60000)  # 替换为目标URL
        print("已加载交易列表页")

        # 4. 主爬取循环
        current_page = 1
        max_pages = 416  # 设置安全限制

        with ThreadPoolExecutor(max_workers=5) as executor:  # 最大5个线程并发执行
            futures = []  # 用于存储每个房产条目抓取的任务

            while current_page <= max_pages:
                print(f"\n▶ 正在处理第 {current_page} 页...")

                # 等待内容加载
                page.wait_for_selector('.cv-structured-list-item', state="attached", timeout=10000)

                # 获取当前页所有房产
                properties = page.locator('.cv-structured-list-item').all()
                print(f"  找到 {len(properties)} 个房产条目")

                # 并行处理每个房产
                for idx, prop in enumerate(properties, 1):
                    futures.append(executor.submit(process_property, prop, idx, current_page, output_file, page))

                # 等待所有任务完成
                for future in futures:
                    future.result()

                # 翻页逻辑
                try:
                    next_button = page.locator('xpath=/html/body/div[2]/div/div/div[5]/div[7]/div/div/div[4]/div/button[2]').first
                    '/html/body/div/main/div[2]/div/div[2]/div[3]/div[3]/div/div[2]/ul/li[8]'
                    if next_button.is_visible(timeout=5000):
                        next_button.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        page.evaluate('(element) => { element.click(); }', next_button.element_handle())
                        page.wait_for_selector('.cv-structured-list-item', state="attached", timeout=15000)
                        current_page += 1
                        print(f"已成功翻到第 {current_page} 页")
                        time.sleep(2)  # 等待页面完全加载
                    else:
                        print("已到达最后一页")
                        break
                except Exception as e:
                    print(f"翻页失败: {str(e)}")
                    break

        # 6. 资源清理
        time.sleep(1)
        context.close()
        browser.close()

        print(f"\n✅ 爬取完成！共处理 {current_page - 1} 页数据")
        print(f"数据已保存到: {output_file}")

# 处理每个房产的函数
def process_property(prop, idx, current_page, output_file, page):
    try:
        prop.scroll_into_view_if_needed()
        time.sleep(0.2)

        # 数据提取
        date = prop.locator('.info-date span').inner_text().strip()  # 成交日期
        name_location = prop.locator('.cv-structured-list-data').nth(1).inner_text().strip()  # 房产名称与位置
        price = prop.locator('.tranPrice').inner_text().strip().replace('$', '')  # 价格
        area = prop.locator('.cv-structured-list-data').nth(5).inner_text().strip()  # 面积
        unit_price = prop.locator('.cv-structured-list-data').nth(6).inner_text().strip()  # 单价
        agency = prop.locator('.label01').inner_text().strip()  # 中介公司

        # 提取图片链接
        image_button = prop.locator('.look-modal').first
        image_button.click()  # 点击查看图片
        time.sleep(1)  # 等待图片加载

        # 假设图片链接是通过某个特定元素展示的
        image_url = page.locator('img[src^="http"]').first.get_attribute('src')  # 获取图片 URL
        print(f"  图片链接: {image_url}")

        # 下载并保存图片
        image_filename = f"image_{current_page}_{idx}.jpg"
        download_image(image_url, image_filename)
        print(f"  ✓ 图片已保存: {image_filename}")

        # 写入数据
        with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                date,
                name_location,
                price,
                area,
                unit_price,
                agency,
                image_filename  # 保存图片文件名或图片链接
            ])

        print(f"  ✓ [{idx}/{current_page}] 已保存: {name_location}")

    except Exception as e:
        print(f"  ✕ 条目 {idx} 处理失败: {str(e)}")
        return

# 下载图片函数
def download_image(url, filename):
    try:
        img_data = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"  图片保存成功: {filename}")
    except Exception as e:
        print(f"  图片下载失败: {str(e)}")

if __name__ == "__main__":
    new_property_scraper()
