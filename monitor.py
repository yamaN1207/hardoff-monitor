import json
import os
from playwright.sync_api import sync_playwright

URL = "https://netmall.hardoff.co.jp/cate/00010012/"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_items():
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # ページ読み込み
        page.goto(URL, wait_until="networkidle")

        # 商品リンク取得
        links = page.query_selector_all('a[href*="/product/"]')

        for a in links:
            name = a.inner_text().strip()
            link = a.get_attribute("href")

            if name and len(name) > 5:
                if not link.startswith("http"):
                    link = "https://netmall.hardoff.co.jp" + link

                items.append(f"{name} | {link}")

        browser.close()

    print("取得件数:", len(items))
    return list(set(items))


def load_old():
    if not os.path.exists("items.json"):
        return []
    with open("items.json", "r") as f:
        return json.load(f)


def save(items):
    with open("items.json", "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def notify(new_items):
    import requests

    message = "🆕 新着商品！\n\n" + "\n".join(new_items[:5])

    requests.post(
        WEBHOOK_URL,
        json={"content": message}
    )


def main():
    new = get_items()
    old = load_old()

    diff = [i for i in new if i not in old]

    if diff:
        notify(diff)

    save(new)


if __name__ == "__main__":
    main()
