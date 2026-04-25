import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://netmall.hardoff.co.jp/cate/00010012/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja-JP,ja;q=0.9",
    "Referer": "https://www.google.com/",
}

WEBHOOK_URL = os.getenv("WEBHOOK_URL")


def get_items():
    session = requests.Session()

    # ① 先にトップページにアクセス（重要）
    session.get("https://netmall.hardoff.co.jp/", headers=HEADERS)

    # ② 本命ページ
    res = session.get(URL, headers=HEADERS)

    print("ステータス:", res.status_code)
    print("HTML長さ:", len(res.text))

    soup = BeautifulSoup(res.text, "html.parser")

    items = []

    for a in soup.select('a[href*="/product/"]'):
        name = a.get_text(strip=True)
        link = a.get("href")

        if name and len(name) > 5:
            if not link.startswith("http"):
                link = "https://netmall.hardoff.co.jp" + link

            items.append(f"{name} | {link}")

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
