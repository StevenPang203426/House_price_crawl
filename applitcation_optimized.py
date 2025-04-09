from playwright.sync_api import sync_playwright
import csv
import time
from datetime import datetime

from tensorflow.python.data.experimental.ops.testing import sleep


# 区域URL字典
REGION_URLS = {

    "港島東-鰂魚涌": "https://www.hkp.com.hk/zh-hk/list/transaction/鰂魚涌-D-10040008",  # NAT
    # 九龍
    "九龍-京士柏": "https://www.hkp.com.hk/zh-hk/list/transaction/京士柏-D-20050004",
    "九龍-九龍站": "https://www.hkp.com.hk/zh-hk/list/transaction/九龍站-D-20050001",
    "九龍-奧運": "https://www.hkp.com.hk/zh-hk/list/transaction/奧運-D-20050008",
    "九龍-太子": "https://www.hkp.com.hk/zh-hk/list/transaction/太子-D-20050006",
    "九龍-油麻地": "https://www.hkp.com.hk/zh-hk/list/transaction/油麻地-D-20050007",
    "九龍-荔枝角": "https://www.hkp.com.hk/zh-hk/list/transaction/荔枝角-D-20060005",
    "九龍-長沙灣": "https://www.hkp.com.hk/zh-hk/list/transaction/長沙灣-D-20060002",
    "九龍-深水埗": "https://www.hkp.com.hk/zh-hk/list/transaction/深水埗-D-20060003",
    "九龍-美孚": "https://www.hkp.com.hk/zh-hk/list/transaction/美孚-D-20060004",
    "九龍-紅磡": "https://www.hkp.com.hk/zh-hk/list/transaction/紅磡-D-20090005",
    "九龍-何文田": "https://www.hkp.com.hk/zh-hk/list/transaction/何文田-D-20090004",
    "九龍-土瓜灣": "https://www.hkp.com.hk/zh-hk/list/transaction/土瓜灣-D-20090003",
    "九龍-九龍城": "https://www.hkp.com.hk/zh-hk/list/transaction/九龍城-D-20090001",
    "九龍-啟德": "https://www.hkp.com.hk/zh-hk/list/transaction/啟德-D-20090006",
    "九龍-新蒲崗": "https://www.hkp.com.hk/zh-hk/list/transaction/新蒲崗-D-20080003",
    "九龍-九龍灣": "https://www.hkp.com.hk/zh-hk/list/transaction/九龍灣-D-20070001",
    "九龍-油塘": "https://www.hkp.com.hk/zh-hk/list/transaction/油塘-D-20070004",
    "九龍-藍田": "https://www.hkp.com.hk/zh-hk/list/transaction/藍田-D-20070005",
    "九龍-坑口": "https://www.hkp.com.hk/zh-hk/list/transaction/坑口-D-20100001",
    "九龍-調景嶺": "https://www.hkp.com.hk/zh-hk/list/transaction/調景嶺-D-20100003",
    "九龍-康城": "https://www.hkp.com.hk/zh-hk/list/transaction/康城-D-20100002",
    "九龍-將軍澳市中心": "https://www.hkp.com.hk/zh-hk/list/transaction/將軍澳市中心-D-20100004",
    "九龍-寶琳": "https://www.hkp.com.hk/zh-hk/list/transaction/寶琳-D-20100005",
    "九龍-清水灣": "https://www.hkp.com.hk/zh-hk/list/transaction/清水灣-D-30100001",
    "九龍-西貢": "https://www.hkp.com.hk/zh-hk/list/transaction/西貢-D-30100002",
    # 新界
    "新界-清水灣": "https://www.hkp.com.hk/zh-hk/list/transaction/清水灣-D-30100001",
    "新界-西貢": "https://www.hkp.com.hk/zh-hk/list/transaction/西貢-D-30100002",
    "新界-沙田": "https://www.hkp.com.hk/zh-hk/list/transaction/沙田-D-30170003",
    "新界-大圍": "https://www.hkp.com.hk/zh-hk/list/transaction/大圍-D-30170002",
    "新界-馬鞍山": "https://www.hkp.com.hk/zh-hk/list/transaction/馬鞍山-D-30170004",
    "新界-大埔": "https://www.hkp.com.hk/zh-hk/list/transaction/大埔-D-30160001",
    "新界-古洞": "https://www.hkp.com.hk/zh-hk/list/transaction/古洞-D-30150003",
    "新界-天水圍": "https://www.hkp.com.hk/zh-hk/list/transaction/天水圍-D-30140003",
    "新界-錦田": "https://www.hkp.com.hk/zh-hk/list/transaction/錦田-D-30140001",
    "新界-元朗市中心": "https://www.hkp.com.hk/zh-hk/list/transaction/元朗市中心-D-30140002",
    "新界-洪水橋": "https://www.hkp.com.hk/zh-hk/list/transaction/洪水橋-D-30140004",
    "新界-掃管笏": "https://www.hkp.com.hk/zh-hk/list/transaction/掃管笏-D-30130003",
    "新界-藍地": "https://www.hkp.com.hk/zh-hk/list/transaction/藍地-D-30130004",
    "新界-屯門碼頭": "https://www.hkp.com.hk/zh-hk/list/transaction/屯門碼頭-D-30130002",
    "新界-屯門市中心": "https://www.hkp.com.hk/zh-hk/list/transaction/屯門市中心-D-30130001",
    "新界-荃灣": "https://www.hkp.com.hk/zh-hk/list/transaction/荃灣-D-30110001",
    "新界-馬灣": "https://www.hkp.com.hk/zh-hk/list/transaction/馬灣-D-30110003",
    "新界-葵涌": "https://www.hkp.com.hk/zh-hk/list/transaction/葵涌-D-30120001",
    "新界-青衣": "https://www.hkp.com.hk/zh-hk/list/transaction/青衣-D-30120002",
    "新界-愉景灣": "https://www.hkp.com.hk/zh-hk/list/transaction/愉景灣-D-30180003",
    "新界-東涌": "https://www.hkp.com.hk/zh-hk/list/transaction/東涌-D-30180002",
    # 港島東
    "港島東-柴灣": "https://www.hkp.com.hk/zh-hk/list/transaction/柴灣-D-10040004",
    "港島東-杏花邨": "https://www.hkp.com.hk/zh-hk/list/transaction/杏花邨-D-10040003",
    "港島東-小西灣": "https://www.hkp.com.hk/zh-hk/list/transaction/小西灣-D-10040005",
    "港島東-筲箕灣": "https://www.hkp.com.hk/zh-hk/list/transaction/筲箕灣-D-10040006",
    # 灣仔區
    "灣仔區-灣仔": "https://www.hkp.com.hk/zh-hk/list/transaction/灣仔-D-10020001",
    # 中西區
    "中西區-中半山": "https://www.hkp.com.hk/zh-hk/list/transaction/中半山-D-10010006",
    "中西區-堅尼地城": "https://www.hkp.com.hk/zh-hk/list/transaction/堅尼地城-D-10010001",
    "中西區-西營盤": "https://www.hkp.com.hk/zh-hk/list/transaction/西營盤-D-10010002",
    "中西區-西半山": "https://www.hkp.com.hk/zh-hk/list/transaction/西半山-D-10010005",
    "中西區-上環": "https://www.hkp.com.hk/zh-hk/list/transaction/上環-D-10010003",
    "中西區-山頂": "https://www.hkp.com.hk/zh-hk/list/transaction/山頂-D-10010007",
    # 南區
    "南區-壽臣山": "https://www.hkp.com.hk/zh-hk/list/transaction/壽臣山-D-10030007",
    "南區-淺水灣": "https://www.hkp.com.hk/zh-hk/list/transaction/淺水灣-D-10030006",
    "南區-鴨脷洲": "https://www.hkp.com.hk/zh-hk/list/transaction/鴨脷洲-D-10030003",
    "九龍-紅磡灣尖東": "https://www.hkp.com.hk/zh-hk/list/transaction/紅磡灣-尖東-D-20050003",  # NAT
    "九龍-尖沙咀佐敦": "https://www.hkp.com.hk/zh-hk/list/transaction/尖沙咀-佐敦-D-20050002",  # NAT
    "九龍-又一村石硤尾": "https://www.hkp.com.hk/zh-hk/list/transaction/又一村-石硤尾-D-20060001",
    "九龍-旺角大角咀": "https://www.hkp.com.hk/zh-hk/list/transaction/搜尋-H-1e92be43",
    "九龍-九龍塘筆架山": "https://www.hkp.com.hk/zh-hk/list/transaction/九龍塘-筆架山-D-20090002",
    "九龍-黃大仙樂富": "https://www.hkp.com.hk/zh-hk/list/transaction/黃大仙-樂富-D-20080001",
    "九龍-鑽石山牛池灣": "https://www.hkp.com.hk/zh-hk/list/transaction/鑽石山-牛池灣-D-20080002",
    "九龍-秀茂坪安達臣": "https://www.hkp.com.hk/zh-hk/list/transaction/秀茂坪-安達臣-D-20070003",
    "九龍-觀塘牛頭角": "https://www.hkp.com.hk/zh-hk/list/transaction/觀塘-牛頭角-D-20070002",
    "新界-九肚山火炭": "https://www.hkp.com.hk/zh-hk/list/transaction/九肚山-火炭-D-30170001",
    "新界-大埔滘白石角": "https://www.hkp.com.hk/zh-hk/list/transaction/大埔滘-白石角-D-30160002",
    "新界-大埔墟太和": "https://www.hkp.com.hk/zh-hk/list/transaction/大埔墟-太和-D-30160003",
    "新界-上水打鼓嶺": "https://www.hkp.com.hk/zh-hk/list/transaction/搜尋-H-8c0f2c7",
    "新界-粉嶺沙頭角": "https://www.hkp.com.hk/zh-hk/list/transaction/搜尋-H-fd09ec4",
    "新界-深井青龍頭": "https://www.hkp.com.hk/zh-hk/list/transaction/深井-青龍頭-D-30110002",
    "新界-大嶼山離島": "https://www.hkp.com.hk/zh-hk/list/transaction/大嶼山-離島-D-30180001",
    "新界-錦繡加州葡萄園": "https://www.hkp.com.hk/zh-hk/list/transaction/錦繡-加州-葡萄園-D-30140005",
    "港島東-北角炮台山": "https://www.hkp.com.hk/zh-hk/list/transaction/北角-炮台山-D-10040002",
    "港島東-寶馬山北角半山": "https://www.hkp.com.hk/zh-hk/list/transaction/寶馬山-北角半山-D-10040007",
    "港島東-太古西灣河": "https://www.hkp.com.hk/zh-hk/list/transaction/太古-西灣河-D-10040001",
    "灣仔區-銅鑼灣天后": "https://www.hkp.com.hk/zh-hk/list/transaction/搜尋-H-2dd6cee0",  # NAT
    "灣仔區-渣甸山大坑": "https://www.hkp.com.hk/zh-hk/list/transaction/渣甸山-大坑-D-10020003",  # NAT
    "灣仔區-跑馬地東半山": "https://www.hkp.com.hk/zh-hk/list/transaction/跑馬地-東半山-D-10020004",  # NAT
    "中西區-中環金鐘": "https://www.hkp.com.hk/zh-hk/list/transaction/搜尋-H-86978425",
    "南區-貝沙灣薄扶林": "https://www.hkp.com.hk/zh-hk/list/transaction/貝沙灣-薄扶林-D-10030002",
    "南區-大潭石澳": "https://www.hkp.com.hk/zh-hk/list/transaction/大潭-石澳-D-10030001",
    "南區-赤柱舂磡角": "https://www.hkp.com.hk/zh-hk/list/transaction/赤柱-舂磡角-D-10030008",
    "南區-黃竹坑深灣": "https://www.hkp.com.hk/zh-hk/list/transaction/黃竹坑-深灣-D-10030005",
    "南區-香港仔田灣": "https://www.hkp.com.hk/zh-hk/list/transaction/香港仔-田灣-D-10030004",
}


def hk_property_scraper():
    with sync_playwright() as p:
        # 浏览器配置
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            timeout=60000
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )

        # 创建总数据文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        master_file = f'hk_properties_all_regions_{timestamp}.csv'

        with open(master_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['区域', '子区域', '房产名称', '位置', '成交日期', '户型', '价格(HKD)', '面积(呎)', '单价', '特色', '房龄', '朝向', '开发商', '几手信息'])

        # 遍历每个区域
        for region_name, url in REGION_URLS.items():
            main_region, sub_region = region_name.split('-', 1)
            page = context.new_page()

            print(f"\n=== 开始爬取区域: {main_region} - {sub_region} ===")

            try:
                # 访问区域页面
                page.goto(url, timeout=60000)
                print(f"已加载: {sub_region} 交易列表页")

                # 创建区域独立文件（可选）
                region_file = f'hk_properties_{main_region}_{sub_region}_{timestamp}.csv'
                with open(region_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        ['区域', '子区域', '房产名称', '位置', '成交日期', '户型', '价格(HKD)', '面积(呎)', '单价',
                         '特色', '房龄', '朝向', '开发商', '几手信息'])

                # 爬取最多50页
                current_page = 1
                max_pages = 50
                total_properties = 0

                while current_page <= max_pages:
                    print(f"\n▶ 正在处理 {sub_region} 第 {current_page} 页...")

                    # 等待内容加载
                    try:
                        page.wait_for_selector('.difilq-4.frWOjp', state="attached", timeout=15000)
                    except:
                        print("等待元素超时，可能已无更多数据")
                        break

                    # 模拟滚动
                    for _ in range(2):
                        page.mouse.wheel(0, 800)
                        time.sleep(0.5)

                    # 获取房产条目
                    properties = page.locator('.difilq-4.frWOjp')
                    count_properties = properties.count()
                    print(f"  找到 {count_properties} 个房产条目")

                    if count_properties == 0:
                        print("没有找到房产条目，可能已到达最后一页")
                        break

                    # 处理每个房产
                    for idx in range(count_properties):
                        if idx == 0: continue
                        prop = properties.nth(idx)
                        try:
                            prop.scroll_into_view_if_needed()
                            time.sleep(0.1)

                            # 提取数据
                            name_elem = prop.locator('.sc-qp0umg-12.gAqyCO')
                            if name_elem.count() > 0:
                                name_text = name_elem.first.inner_text().strip()
                                name_parts = [p.strip() for p in name_text.split('\n') if p.strip()]
                                prop_name = name_parts[0] if len(name_parts) > 0 else 'N/A'
                                location = name_parts[1] if len(name_parts) > 1 else 'N/A'
                            else:
                                prop_name = 'N/A'
                                location = 'N/A'

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


                            ##
                            try:
                                # 获取当前页面
                                main_page = page

                                # 点击房产链接并等待新页面打开
                                link = prop.locator('a')
                                link.click()

                                # 等待新页面加载
                                new_page = page.context.wait_for_event('page')  # 等待新页面打开

                                # 确保新页面已完全加载
                                new_page.wait_for_selector('.sc-zu92u1-3.sc-zu92u1-5.sc-zu92u1-6.lkhdrh',
                                                           state="attached", timeout=15000)

                                # 获取房龄和朝向等详细信息
                                age = new_page.locator(
                                    '.sc-zu92u1-4.sc-zu92u1-7.piXPP').inner_text().strip() if new_page.locator(
                                    '.sc-zu92u1-4.sc-zu92u1-7.piXPP').count() > 0 else 'N/A'
                                orientation = new_page.locator(
                                    '.sc-zu92u1-4.sc-zu92u1-7.geTrgf').inner_text().strip() if new_page.locator(
                                    '.sc-zu92u1-4.sc-zu92u1-7.geTrgf').count() > 0 else 'N/A'
                                #.sc-13cmw9h-4.kEtHKR
                                # developer_element.text_content().strip()
                                if new_page.locator('.sc-13cmw9h-4.kEtHKR').count() > 0:
                                    # 如果找到开发商信息，并且该信息是多行的
                                    developer_text = new_page.locator(
                                        '.sc-13cmw9h-4.kEtHKR').first.text_content().strip()

                                    # 按换行符分割开发商信息
                                    developer_list = developer_text.split('\n')  # 根据换行符分割文本

                                    # 提取第二个开发商名称（如果有多个开发商）
                                    developer = developer_list[1].strip() if len(developer_list) > 1 else 'N/A'
                                elif new_page.locator('.sc-1gd06yc-0.jkqPxV').count() > 1:
                                    # 如果找到多个开发商信息，选择第二个
                                    developers = new_page.locator('.sc-1gd06yc-0.jkqPxV')

                                    # 使用 text_content 来获取开发商信息，并根据换行符分割
                                    developer_text = developers.nth(
                                        1).text_content().strip() if developers.count() > 1 else 'N/A'

                                    # 分割开发商信息并提取第二个开发商（按换行符分割）
                                    developer_list = developer_text.split('\n')  # 根据换行符分割文本
                                    developer = developer_list[1].strip() if len(developer_list) > 1 else 'N/A'
                                else:
                                    # 如果都没有找到开发商信息，返回 'N/A'
                                    developer = 'N/A'

                                ownership = new_page.locator(
                                    '.sc-1p803b8-34.hzeNwL').first.inner_text().strip() if new_page.locator(
                                    '.sc-1p803b8-34.hzeNwL').count() > 0 else 'N/A'

                                # 返回原页面
                                main_page.bring_to_front()

                                # 关闭新页面，释放资源
                                new_page.close()

                            except Exception as e:
                                print(f"处理条目时发生错误: {e}")

                            ##



                            # 写入数据
                            row_data = [
                                main_region,
                                sub_region,
                                prop_name,
                                location,
                                date,
                                house_type,
                                full_price,
                                area,
                                unit_price,
                                features,
                                age,
                                orientation,
                                developer,
                                ownership
                            ]

                            # 写入区域文件
                            with open(region_file, 'a', newline='', encoding='utf-8-sig') as f:
                                writer = csv.writer(f)
                                writer.writerow(row_data)

                            # 写入总文件
                            with open(master_file, 'a', newline='', encoding='utf-8-sig') as f:
                                writer = csv.writer(f)
                                writer.writerow(row_data)

                            total_properties += 1
                            print(f"  ✓ [{total_properties}] 已保存: {prop_name}")

                        except Exception as e:
                            print(f"  ✕ 条目处理失败: {str(e)}")
                            continue




                    # 使用你原来的翻页逻辑
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
                                page.goto(f"{url}?page={next_page}", timeout=15000)
                                current_page = next_page
                                print(f"通过URL直接跳转到第 {current_page} 页")
                                time.sleep(2)
                            else:
                                print("已达到最大页数限制")
                                break
                        except:
                            print("所有翻页方案均失败")
                            break

                print(f"\n✅ 完成 {sub_region} 爬取! 共获取 {total_properties} 条数据")
                print(f"区域数据已保存到: {region_file}")

            except Exception as e:
                print(f"!!! 处理区域 {sub_region} 时发生严重错误: {str(e)}")
            finally:
                page.close()
                time.sleep(1)

        # 关闭浏览器
        context.close()
        browser.close()

        print(f"\n🎉 所有区域爬取完成! 主数据文件: {master_file}")


if __name__ == "__main__":
    hk_property_scraper()