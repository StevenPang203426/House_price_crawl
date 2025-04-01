from playwright.sync_api import sync_playwright
import requests
import time


def download_images_from_page():
    with sync_playwright() as p:
        # 1. 启动浏览器并加载页面
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

        # 访问目标页面
        page.goto("https://hk.centanet.com/findproperty/zh-cn/list/transaction", timeout=60000)  # 替换为目标 URL
        print("已加载页面")

        # 2. 获取所有触发图片显示的按钮并点击
        buttons = page.locator('.look-modal').all()  # 假设按钮的 class 为 .look-modal
        print(f"找到 {len(buttons)} 个查看图片的按钮")

        # 3. 点击按钮并获取图片
        for idx, button in enumerate(buttons, 1):
            button.click()  # 点击按钮显示图片
            time.sleep(2)  # 等待图片加载

            # 等待图片加载完成
            image = page.locator('img[src^="https://hk.centanet.com/imgresize"]').first  # 图片的 src 属性包含该字符串
            image_url = image.get_attribute('src')  # 获取图片 URL
            if image_url:
                print(f"  图片 {idx} 链接: {image_url}")

                # 下载图片
                image_filename = f"image_{idx}.jpg"
                download_image(image_url, image_filename)

            # 关闭图片查看器（如果有关闭按钮）
            close_button = page.locator('.el-icon-close').first  # 假设关闭按钮的类名是 .el-icon-close
            close_button.click()  # 关闭图片查看器
            time.sleep(1)  # 等待关闭操作

        # 清理资源
        time.sleep(1)
        context.close()
        browser.close()

        print(f"\n✅ 图片下载完成！")


def download_image(url, filename):
    try:
        img_data = requests.get(url).content
        with open(filename, 'wb') as f:
            f.write(img_data)
        print(f"  图片已保存: {filename}")
    except Exception as e:
        print(f"  图片下载失败: {str(e)}")


if __name__ == "__main__":
    download_images_from_page()
