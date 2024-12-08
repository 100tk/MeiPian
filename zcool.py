import httpx
from bs4 import BeautifulSoup

url = "https://www.zcool.com.cn/u/23024973"


def get_html(url):
    with httpx.Client() as client:
        response = client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.find_all("section")
        for i in data:
            print(i)


get_html(url)
