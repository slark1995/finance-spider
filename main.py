import asyncio
from playwright.async_api import async_playwright
import csv
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("正在访问东方财富网...")
        url = "https://finance.eastmoney.com/a/cgnjj.html"
        try:
            # 使用 domcontentloaded 减少等待时间
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 等待新闻列表容器出现
            print("等待新闻列表加载...")
            await page.wait_for_selector("#newsListContent", timeout=20000)
            
            # 额外等待一小会儿确保 JS 执行完毕
            await asyncio.sleep(2)
            
            # 提取新闻数据
            news_items = await page.query_selector_all("#newsListContent li")
            print(f"找到 {len(news_items)} 条新闻项")
            
            articles = []
            for item in news_items:
                title_element = await item.query_selector(".title a")
                if not title_element:
                    continue
                
                title = await title_element.inner_text()
                link = await title_element.get_attribute("href")
                
                time_element = await item.query_selector(".time")
                publish_time = await time_element.inner_text() if time_element else ""
                
                info_element = await item.query_selector(".info")
                summary = await info_element.inner_text() if info_element else ""
                
                if title.strip():
                    articles.append({
                        "标题": title.strip(),
                        "发布时间": publish_time.strip(),
                        "链接": link,
                        "摘要": summary.strip()
                    })
            
            return articles
        except Exception as e:
            print(f"运行出错: {e}")
            return []
        finally:
            await browser.close()

def save_to_csv(data, filename="eastmoney_news.csv"):
    if not data:
        print("没有数据可保存")
        return
    
    fieldnames = ["标题", "发布时间", "链接", "摘要"]
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"数据已成功保存至 {filename}")

if __name__ == "__main__":
    # 使用更现代的 asyncio 运行方式
    news_data = asyncio.run(run())
    
    if news_data:
        print(f"抓取成功，共获取到 {len(news_data)} 条新闻")
        save_to_csv(news_data)
    else:
        print("抓取失败")
