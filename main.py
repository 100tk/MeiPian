import re
import json
import httpx
import sqlite3
import logging
from datetime import datetime
from bs4 import BeautifulSoup, ResultSet, Tag
from pathlib import Path
from rich.progress import Progress, TextColumn, BarColumn, FileSizeColumn, SpinnerColumn
from concurrent.futures import ThreadPoolExecutor
import threading
import pyjson5


# 配置日志记录，日志文件名为error.log，日志级别为ERROR，日志格式为：日期时间 - 日志级别 - 日志消息
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    encoding="utf-8",
)

BASE_PATH = Path("D:\\图片")
look = threading.Lock()


def re_name(file_name):
    return re.sub(r'[\\/\s:*?"<>|…]+|\.{2,}', "", file_name).strip()


def re_nikename(nike_name):
    return re.sub(r'[\\/\s:*?"<>|…]+|\.{2,}', "？", nike_name).strip()


def download(client, url, filename, description, folder, retries=3):
    try:
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / filename
        for attempt in range(retries):
            try:
                with client.stream("GET", url) as response:
                    response: httpx.Response
                    if response.headers.get("content-type") == "application/json":
                        print("返回 JSON，跳过下载。")
                        logging.error(f"URL {url} 返回 JSON，跳过下载。")
                        return
                    total = int(response.headers.get("content-length", 0))
                    with look:
                        with Progress(
                            TextColumn(
                                "[progress.description]{task.description}",
                            ),
                            SpinnerColumn(),
                            BarColumn(),
                            FileSizeColumn(),
                        ) as progress:
                            task_id = progress.add_task(
                                description=f"正在下载 [bold red]{description}[/bold red]> [blue]{filename}[/blue]",
                                total=total,
                            )
                            with open(filepath, "wb") as file:
                                for chunk in response.iter_bytes():
                                    file.write(chunk)
                                    progress.update(task_id, advance=len(chunk))
                break
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError) as e:
                logging.error(f"下载 {url} 时发生错误: {e}，重试 {attempt + 1}/{retries}")
                print(f"下载 {url} 时发生错误: {e}，重试 {attempt + 1}/{retries}")
                if attempt + 1 == retries:
                    logging.error(f"下载 {url} 失败，已达到最大重试次数。")
                    print(f"下载 {url} 失败，已达到最大重试次数。")
    except Exception as e:
        logging.error(e)
        print(e)


def fetch_articles(user_id):
    con = sqlite3.connect("美篇.db")
    cur = con.cursor()
    try:
        cur.execute(
            """
                create table if not exists article
                (
                    user_id       integer                            not null,
                    mask_id       text primary key                   not null,
                    create_time   text                               not null,
                    url           text                               not null,
                    title         text                               not null,
                    cover_img_url text                               not null,
                    is_down       integer default 0                  not null,
                    check ( is_down in (0, 1))
                );
            """
        )

        url = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
        params = {"last_mask_id": 0}

        with httpx.Client() as client:
            while True:
                try:
                    response = client.get(url=url, params=params)
                    data = response.json()
                    page = data["data"]
                    items = [
                        {
                            "user_id": user_id,
                            "mask_id": item["mask_id"],
                            "create_time": datetime.fromtimestamp(item["create_time"]).strftime("%Y-%m-%d-%H-%M"),
                            "url": f"https://www.meipian.cn/{item['mask_id']}",
                            "title": item["title"].replace(" ", ""),
                            "cover_img_url": item["cover_img_url"],
                        }
                        for item in page
                    ]

                    cur.executemany(
                        """
                            INSERT INTO article (user_id,mask_id,create_time,url,title,cover_img_url)
                            VALUES (:user_id,:mask_id,:create_time,:url,:title,:cover_img_url)
                        """,
                        items,
                    )
                    con.commit()
                    print("插入数据中----------------------------")

                    if not page or len(page) < 20:
                        break
                    params["last_mask_id"] = page[-1]["mask_id"]

                except httpx.HTTPStatusError as e:
                    logging.error(f"HTTP状态错误:{e}")
                    print(f"HTTP状态错误:{e}")
                except json.JSONDecodeError as e:
                    logging.error(f"JSON解析错误:{e}")
                    print(f"JSON解析错误:{e}")
                except sqlite3.Error as e:
                    logging.error("数据已存在数据库中，请重新输入。")
                    print("数据已存在数据库中，请重新输入。")
                    return False
    finally:
        con.close()
    return True


def download_content(user_id):
    headers = {"User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"}
    try:
        with sqlite3.connect("美篇.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url,title,create_time FROM article WHERE user_id=?", (user_id,))
            with httpx.Client() as client:
                for url, title, create_time in get_row(cursor):
                    response = client.get(url=url, headers=headers)
                    soup = BeautifulSoup(response.text, "html.parser")
                    scripts: ResultSet[Tag] = soup.find_all("script")
                    for script in scripts:
                        if script.text:
                            data = re.search(
                                r"ARTICLE_DETAIL\s=\s({.*});|BLADE_ARTICLE_JSON\s=\s({.*})", script.text, re.S
                            )
                            if data:
                                data = data.group(1) or data.group(2)
                                data = pyjson5.loads(data)
                                nickname = data["author"]["nickname"]
                                nickname = re_nikename(nickname)
                                title = re_name(title)
                                folder = BASE_PATH / nickname / f"{create_time}{title}"
                                content = [
                                    item for item in data["content"] if item.get("img_url") or item.get("video_url")
                                ]
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
        logging.error(f"发生错误: {e}")
        print(f"发生错误: {e}")


def get_row(cursor):
    row = cursor.fetchone()
    while row is not None:
        yield row
        row = cursor.fetchone()


def main():
    while True:
        user_input = input("请输入用户ID或URL (直接回车退出)：")
        if not user_input:
            break

        match = re.match(r"(https?://)?www\.meipian\.cn/c/(\d+)", user_input)
        if match:
            user_id = int(match.group(2))
        elif user_input.isdigit():
            user_id = int(user_input)
        else:
            print("输入格式错误，请重新输入。")
            continue

        if fetch_articles(user_id):
            download_content(user_id)


if __name__ == "__main__":
    main()
