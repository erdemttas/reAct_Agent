from langchain.agents import Tool
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()

 # burada normalde birden fazla araç vardı ama ben görselleştirme ile ilgili kısımları eklemedim, ajanımız normalde birden çok araca erişebilecekti.

def analyze_webpage(target_url):
    response = requests.get(target_url)
    html_content = response.text

    soup = BeautifulSoup(html_content, "html.parser")
    stripped_content = soup.get_text()

    if len(stripped_content) > 4000:
        stripped_content = stripped_content[:4000]

    return stripped_content


#agentlar için uygun formata getiriyoruz web scraping işlemini.
def get_web_tool():
    return Tool(
        name="get webpage",
        func=analyze_webpage,
        description="useful for when you need to get the http from a specific webpage"
    )

"""Kendi kişisel araçlarını agentlar ile kullanabilirsin, web scraping olur, görsel üretme olur
    multilanguages çoklu dil çevirisi yapan bir agent yapılabilir."""



