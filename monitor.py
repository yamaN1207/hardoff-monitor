import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://netmall.hardoff.co.jp/cate/00010012/"
HEADERS = {"User-Agent": "Mozilla/5.0"}

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def get_items():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    items = []
    for item in soup.select(".item-name"):
        items.append(item.text.strip())

    return items

def load_old():
    if not os.path.exists("items.json"):
        return []
    with open("items.json", "r") as f:
        return json.load(f)

def save(items):
    with open("items.json", "w") as f:
        json.dump(items, f)

def notify(new_items):
    message = "🆕 新着商品！\n" + "\n".join(new_items[:5])

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
