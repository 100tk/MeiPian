import httpx
import json
import os
import asyncio
from bs4 import BeautifulSoup


# 创建异步下载函数
async def download_file(client, url, folder):
    try:
        response = await client.get(url)
        response.raise_for_status()  # 如果响应状态码不是 200，将引发异常

        # 获取文件名
        filename = os.path.basename(url)
        filepath = os.path.join(folder, filename)

        # 保存文件
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"下载完成: {filepath}")

    except Exception as e:
        print(f"下载失败: {url}，错误: {e}")


async def main():
    async with httpx.AsyncClient() as client:
        url = "https://www.meipian.cn/25m1pioo"
        headers = {"User-Agent": "Opera/12.02 (Android 4.1; Linux; Opera Mobi/ADR-1111101157; U; en-US) Presto/2.9.201 Version/12.02"}
        response = await client.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # 找到包含文章数据的textarea元素
        textarea = soup.find("textarea", attrs={"data-article-json": "Blade_ContentJson"})
        # 将textarea中的JSON数据解析为Python对象
        contents = json.loads(textarea.text)

        img_urls = []
        video_urls = []

        for content in contents:
            if content.get("img_url") is not None:
                img_urls.append(content["img_url"])
            elif content.get("video_url") is not None:
                video_urls.append(content["video_url"])

        # 创建文件夹存储下载的文件
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)

        # 创建异步任务
        tasks = []
        for img_url in img_urls:
            tasks.append(download_file(client, img_url, download_folder))
        for video_url in video_urls:
            tasks.append(download_file(client, video_url, download_folder))

        # 并发执行下载任务
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
