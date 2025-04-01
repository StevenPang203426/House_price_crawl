from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime


def hk_property_scraper():
    with sync_playwright() as p:
        # 1. 浏览器配置
        browser = p.chromium.launch(
            headless=False,  # 调试时可设为False，方便查看爬取过程
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
        output_file = f'hk_properties_{timestamp}.csv'

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['房产名称', '位置', '成交日期', '户型', '价格(HKD)', '面积(呎)', '单价', '特色'])

        # 3. 访问目标页面
        page.goto("https://www.hkp.com.hk/zh-hk/list/transaction", timeout=60000)
        print("已加载交易列表页")

        # 4. 主爬取循环
        current_page = 1
        max_pages = 416  # 安全限制

        while current_page <= max_pages:
            print(f"\n▶ 正在处理第 {current_page} 页...")

            # 等待内容加载：可根据页面结构做微调
            page.wait_for_selector('.difilq-4.frWOjp', state="attached", timeout=10000)

            # 模拟人类滚动行为：可根据实际情况增删次数
            for _ in range(2):
                page.mouse.wheel(0, 800)
                time.sleep(1)

            # 获取当前页所有房产
            properties = page.locator('.difilq-4.frWOjp')
            count_properties = properties.count()
            print(f"  找到 {count_properties} 个房产条目")

            # 处理每个房产
            for idx in range(count_properties):
                if idx == 0: continue
                prop = properties.nth(idx)
                try:
                    prop.scroll_into_view_if_needed()
                    time.sleep(0.2)

                    # -----------------------------
                    # 提取数据
                    # -----------------------------

                    # 1) 房产名称、位置
                    name_elem = prop.locator('.sc-qp0umg-12.gAqyCO')
                    if name_elem.count() > 0:
                        name_text = name_elem.first.inner_text().strip()
                        name_parts = [p.strip() for p in name_text.split('\n') if p.strip()]
                        prop_name = name_parts[0] if len(name_parts) > 0 else 'N/A'
                        location = name_parts[1] if len(name_parts) > 1 else 'N/A'
                    else:
                        prop_name = 'N/A'
                        location = 'N/A'

                    # 2) 成交日期（只取第一个出现的）
                    # 使用CSS选择器（更简洁）
                    css_selector = f'#__next > main > div.sc-1xa3s3j-1.hBUjWI > div > div.rmc-tabs-content-wrap > div.rmc-tabs-pane-wrap-active > div.difilq-3.ljLfya > div > div.infinite-scroll-component__outerdiv > div > div > div:nth-child(2) > div:nth-child({idx + 1}) > div > a > div:nth-child(1)'

                    date_element = page.locator(css_selector)
                    date = date_element.inner_text().strip() if date_element.count() > 0 else 'N/A'

                    # 3) 户型、面积、单价等
                    type_elems = prop.locator('.sc-qp0umg-10.dKaBvA')
                    house_type = type_elems.nth(0).inner_text().strip() if type_elems.count() > 0 else 'N/A'
                    area = type_elems.nth(1).inner_text().strip() if type_elems.count() > 1 else 'N/A'
                    unit_price = type_elems.nth(2).inner_text().strip() if type_elems.count() > 2 else 'N/A'

                    # 4) 价格及单位
                    price_elem = prop.locator('.sc-oklxvf-6.lfWa-DB')
                    if price_elem.count() > 0:
                        price = price_elem.first.inner_text().strip()
                    else:
                        price = 'N/A'

                    unit_elem = prop.locator('.sc-oklxvf-7.igTSok.case-price-unit')
                    if unit_elem.count() > 0:
                        price_unit = unit_elem.first.inner_text().strip()
                        full_price = f"{price} {price_unit}"
                    else:
                        full_price = price

                    # 5) 特色
                    feature_spans = prop.locator('.sc-qp0umg-13.gfFjGP span:not(.jrzAg)')
                    features_texts = []
                    feature_count = feature_spans.count()
                    for i in range(feature_count):
                        features_texts.append(feature_spans.nth(i).inner_text().strip())
                    features = ' | '.join(features_texts) if features_texts else 'N/A'

                    # -----------------------------
                    # 写入 CSV
                    # -----------------------------
                    with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            prop_name,
                            location,
                            date,
                            house_type,
                            full_price,
                            area,
                            unit_price,
                            features
                        ])
                    print(f"  ✓ [{idx + 1}/{count_properties}] 已保存: {prop_name}")

                except Exception as e:
                    print(f"  ✕ 条目 {idx + 1} 处理失败: {str(e)}")
                    continue

            # 5. 翻页逻辑
            if current_page <= 3:
                next_XPath = 'xpath=/html/body/div/main/div[2]/div/div[2]/div[3]/div[3]/div/div[2]/ul/li[8]/a'
            else:
                next_XPath = 'xpath=/html/body/div/main/div[2]/div/div[2]/div[3]/div[3]/div/div[2]/ul/li[9]/a'

            try:
                next_button = page.locator(next_XPath).first
                if next_button.is_visible(timeout=5000):
                    is_disabled = next_button.get_attribute('aria-disabled')
                    if is_disabled != 'true':
                        print("正在翻到下一页...")
                        next_button.scroll_into_view_if_needed()
                        time.sleep(0.5)

                        page.evaluate('(element) => { element.click(); }', next_button.element_handle())

                        page.wait_for_selector('.difilq-4.frWOjp', state="attached", timeout=15000)
                        current_page += 1
                        print(f"已成功翻到第 {current_page} 页")
                        time.sleep(2)
                    else:
                        print("已到达最后一页 (按钮禁用)")
                        break
                else:
                    print("下一页按钮不可见或不存在")
                    break
            except Exception as e:
                print(f"翻页失败: {str(e)}")
                try:
                    if current_page < max_pages:
                        next_page = current_page + 1
                        page.goto(f"https://www.hkp.com.hk/zh-hk/list/transaction?page={next_page}", timeout=15000)
                        current_page = next_page
                        print(f"通过URL直接跳转到第 {current_page} 页")
                        time.sleep(2)
                    else:
                        print("已达到最大页数限制")
                        break
                except:
                    print("所有翻页方案均失败")
                    break

        # 6. 资源清理
        time.sleep(1)
        context.close()
        browser.close()

        print(f"\n✅ 爬取完成！共处理 {current_page - 1} 页数据")
        print(f"数据已保存到: {output_file}")


if __name__ == "__main__":
    hk_property_scraper()
