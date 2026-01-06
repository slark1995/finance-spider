import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_zhihu(page):
    print("Scraping Zhihu Hot...")
    try:
        await page.goto("https://www.zhihu.com/hot", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        
        # 根据 browser_view 的结果，条目在 section 标签中
        items = await page.query_selector_all("section")
        print(f"Found {len(items)} sections on Zhihu Hot")
        
        results = []
        for item in items[:15]:
            title_el = await item.query_selector("h2")
            desc_el = await item.query_selector("p")
            link_el = await item.query_selector("a")
            
            title = await title_el.inner_text() if title_el else "No Title"
            desc = await desc_el.inner_text() if desc_el else "No Description"
            link = await link_el.get_attribute("href") if link_el else ""
            
            if link and not link.startswith("http"):
                link = "https://www.zhihu.com" + link
                
            results.append({
                "source": "Zhihu Hot",
                "title": title.strip(),
                "description": desc.strip()[:100] + "...",
                "link": link
            })
        return results
    except Exception as e:
        print(f"Error scraping Zhihu: {e}")
        return []

async def scrape_xueqiu(page):
    print("Scraping Xueqiu...")
    try:
        # 尝试访问雪球的热门页面
        await page.goto("https://xueqiu.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(5)
        
        # 抓取 Home_feed-item 类的 div
        items = await page.query_selector_all("div[class*='Home_feed-item']")
        print(f"Found {len(items)} items on Xueqiu")
        
        results = []
        for item in items[:10]:
            title_el = await item.query_selector("h3, a[class*='title']")
            desc_el = await item.query_selector("div[class*='description'], div[class*='content']")
            link_el = await item.query_selector("a")
            
            title = await title_el.inner_text() if title_el else "No Title"
            desc = await desc_el.inner_text() if desc_el else "No Description"
            link = await link_el.get_attribute("href") if link_el else ""
            
            if link and not link.startswith("http"):
                link = "https://xueqiu.com" + link
                
            results.append({
                "source": "Xueqiu",
                "title": title.strip(),
                "description": desc.strip()[:100] + "...",
                "link": link
            })
        return results
    except Exception as e:
        print(f"Error scraping Xueqiu: {e}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        zhihu_data = await scrape_zhihu(page)
        xueqiu_data = await scrape_xueqiu(page)
        
        all_data = zhihu_data + xueqiu_data
        
        keys = ["source", "title", "description", "link"]
        with open("/home/ubuntu/forum_news_final.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_data)
            
        print(f"Successfully scraped {len(all_data)} items and saved to forum_news_final.csv")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
