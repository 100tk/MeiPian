import httpx
import json
from bs4 import BeautifulSoup

def main():
    with httpx.Client() as client:
        url = 'https://www.meipian.cn/4fnf3f9h'
        headers = {'User-Agent': 'Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10'}
        response = client.get(url=url, headers=headers) 
        soup = BeautifulSoup(response.text, 'html.parser')
        # 找到包含文章数据的textarea元素
        textarea = soup.find('textarea',attrs={'data-article-json':'Blade_ContentJson'})
        # 将textarea中的JSON数据解析为Python对象
        contents = json.loads(textarea.text)
        img = []  # 用于存储找到的图片URL
        video = []  # 用于存储找到的视频URL
        for content in contents: 
            if content.get('img_url') is not None:  # 如果content中包含img_url属性，说明是图片
                img.append(content['img_url'])
            elif content.get('video_url') is not None:  # 如果content中包含video_url属性，说明是视频
                video.append(content['video_url'])

if __name__ == '__main__':
    main()