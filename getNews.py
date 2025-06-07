import os
import schedule
import datetime as dt
from pocketbaseorm import PocketbaseORM
from dotenv import load_dotenv
load_dotenv()
pb_news = PocketbaseORM(os.getenv("PB_URL"), os.getenv("PB_EMAIL"), os.getenv("PB_PASSWORD"), "news")
pb_news_keywords = PocketbaseORM(os.getenv("PB_URL"), os.getenv("PB_EMAIL"), os.getenv("PB_PASSWORD"), "news_keywords")

def get_all_keywords():
    results = pb_news_keywords.get_items(perPage=999)
    keywords = set()
    for item in results:
        if item.keyword is not None:
            keywords.add(item.keyword)
    return list(keywords)

def fetch_news(query):
    import requests
    url = f"https://searxng.hiblazar.com/search?q={query}&format=json&timerange=1d&categories=news&lang=en"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching news: {response.status_code}")
        return None

def get_post_news():
    
    keywords = get_all_keywords()
    for keyword in keywords:
        print(f"Fetching news for keyword: {keyword}")
        current_news = fetch_news(keyword)
        if current_news and "results" in current_news:
            for item in current_news["results"]:
                if 'publishedDate' in item:
                    published_date = dt.datetime.fromisoformat(item['publishedDate'].replace("Z", "+00:00"))
                else:
                    published_date = dt.date.today()
                data = {
                    "keyword": keyword,
                    "title": item["title"],
                    "content": item["content"],
                    "url": item["url"],
                    "date": published_date.strftime('%Y-%m-%d'),
                }
                response = pb_news.add_item(data)
                if response == "Error":
                    pass
                    # print(f"Error adding item: {item['title']}")
                else:
                    print(f"Added item: {item['title']} on {published_date.strftime('%Y-%m-%d')}")
        else:
            print(f"No news found for keyword: {keyword}")

#schedule.every().day.at("05:00").do(getNews)
while True:
	#schedule.run_pending()
    get_post_news()
    time.sleep(60 * 15)
    
