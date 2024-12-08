import re
import httpx
import pyjson5
from bs4 import BeautifulSoup, ResultSet, Tag
from pathlib import Path
from rich.progress import Progress, TextColumn, BarColumn, FileSizeColumn, SpinnerColumn
from concurrent.futures import ThreadPoolExecutor
import threading

BASE_PATH = Path("D:\\图片")

look = threading.Lock()


def re_name(file_name):
    return re.sub(r'[\\/:*?"<>|…]+|\.+', "", file_name).strip()


def re_nikename(nike_name):
    return re.sub(r'[\\/:*?"<>|…]+|\.+', "？", nike_name).strip()


def download(client, url, filename, description, folder):
    try:
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / filename
        with client.stream("GET", url) as response:
            response: httpx.Response
            total = int(response.headers.get("content-length", 0))
            with look:
                with Progress(
                    TextColumn("[progress.description]{task.description}"),
                    SpinnerColumn(),
                    BarColumn(),
                    FileSizeColumn(),
                ) as progress:
                    with open(filepath, "wb") as file:
                        task_id = progress.add_task(
                            description=f"正在下载 [bold red]{description}[/bold red] >>> [blue]{filename}[/blue]",
                            total=total,
                        )
                        for chunk in response.iter_bytes():
                            file.write(chunk)
                            progress.update(task_id, advance=len(chunk))
    except Exception as e:
        print(e)


def main():
    headers = {"User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"}
    url = "https://www.meipian.cn/"
    try:
        with httpx.Client() as client:
            response = client.get(url=url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            scripts: ResultSet[Tag] = soup.find_all("script")
            for script in scripts:
                if script.text:
                    data = re.search(r"ARTICLE_DETAIL\s=\s({.*});|BLADE_ARTICLE_JSON\s=\s({.*})", script.text, re.S)
                    if data:
                        data = data.group(1) or data.group(2)
                        data = pyjson5.loads(data)
                        nickname = data["author"]["nickname"]
                        nickname = re_nikename(nickname)
                        title = re_name(title)
                        folder = BASE_PATH / nickname / f"{create_time}{title}"
                        content = [item for item in data["content"] if item.get("img_url") or item.get("video_url")]
                        tasks = []
                        for count, item in enumerate(content, start=1):
                            if item.get("img_url"):
                                img_url = item["img_url"]
                                img_filename = f"{count}-{title}.jpg"
                                if img_url.endswith(".heic"):
                                    img_url += "~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg"
                                tasks.append((client, img_url, img_filename, "图片", folder))
                            if item.get("video_url"):
                                video_url = item["video_url"]
                                video_filename = f"{count}-{title}.mp4"
                                tasks.append((client, video_url, video_filename, "视频", folder))

                        with ThreadPoolExecutor(max_workers=6) as executor:
                            executor.map(lambda args: download(*args), tasks)

    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
