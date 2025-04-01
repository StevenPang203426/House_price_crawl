from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime


def hk_property_scraper():
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

            # 等待内容加载
            page.wait_for_selector('.difilq-4.frWOjp', state="attached", timeout=10000)

            # 模拟人类滚动行为
            for _ in range(2):
                page.mouse.wheel(0, 800)
                time.sleep(1)

            # 获取当前页所有房产
            properties = page.locator('.difilq-4.frWOjp').all()
            print(f"  找到 {len(properties)} 个房产条目")

            # 处理每个房产
            for idx, prop in enumerate(properties, 1):
                try:
                    prop.scroll_into_view_if_needed()
                    time.sleep(0.2)

                    # 数据提取
                    name = prop.locator('.sc-qp0umg-12.gAqyCO').inner_text().strip()
                    date = prop.locator('.sc-qp0umg-10.dUvXnm').first.inner_text()

                    # 分割名称和位置
                    name_parts = [p.strip() for p in name.split('\n') if p.strip()]
                    prop_name = name_parts[0] if name_parts else 'N/A'
                    location = name_parts[1] if len(name_parts) > 1 else ''

                    # 提取其他信息
                    type_elems = prop.locator('.sc-qp0umg-10.dKaBvA').all()
                    details = {
                        'house_type': type_elems[0].inner_text() if len(type_elems) > 0 else 'N/A',
                        'area': type_elems[1].inner_text() if len(type_elems) > 1 else 'N/A',
                        'unit_price': type_elems[2].inner_text() if len(type_elems) > 2 else 'N/A',
                        'price': prop.locator('.sc-oklxvf-6.lfWa-DB').inner_text(),
                        'features': ' | '.join([
                            f.inner_text()
                            for f in prop.locator('.sc-qp0umg-13.gfFjGP span:not(.jrzAg)').all()
                        ])
                    }

                    # 写入数据
                    with open(output_file, 'a', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            prop_name,
                            location,
                            date,
                            details['house_type'],
                            details['price'],
                            details['area'],
                            details['unit_price'],
                            details['features']
                        ])

                    print(f"  ✓ [{idx}/{len(properties)}] 已保存: {prop_name}")

                except Exception as e:
                    print(f"  ✕ 条目 {idx} 处理失败: {str(e)}")
                    continue

            # 5. 专用翻页逻辑 - 针对您提供的按钮结构
            # 替换原来的翻页代码部分
            # 检查是否可以找到并点击下一页按钮
            # 翻页逻辑
            if current_page <= 3:
                next_XPath = 'xpath=/html/body/div/main/div[2]/div/div[2]/div[3]/div[3]/div/div[2]/ul/li[8]/a'
            else :
                next_XPath = 'xpath=/html/body/div/main/div[2]/div/div[2]/div[3]/div[3]/div/div[2]/ul/li[9]/a'
            try:
                # 使用 XPath 定位到下一页按钮
                next_button = page.locator(next_XPath
                    ).first

                # 确保按钮可见且未被禁用
                if next_button.is_visible(timeout=5000):
                    is_disabled = next_button.get_attribute('aria-disabled')
                    if is_disabled != 'true':
                        print("正在翻到下一页...")
                        next_button.scroll_into_view_if_needed()
                        time.sleep(0.5)

                        # 使用 JavaScript 点击按钮
                        page.evaluate('(element) => { element.click(); }', next_button.element_handle())

                        # 等待新页面加载
                        page.wait_for_selector('.difilq-4.frWOjp', state="attached", timeout=15000)
                        current_page += 1
                        print(f"已成功翻到第 {current_page} 页")
                        time.sleep(2)  # 等待页面完全加载
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