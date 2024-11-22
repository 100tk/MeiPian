import json
import httpx
import re
import sqlite3


def get_input():
    while True:
        input_str = input("输入用户ID或主页URL：")
        if input_str.isdigit():
            return input_str
        match = re.match(r"https?://www\.meipian\.cn/c/(\d+)", input_str)
        if match:
            return match.group(1)
        else:
            print("输入无效，请重新输入。")


def main():
    with httpx.Client() as client:
        user_id = get_input()
        url = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
        headers = {
            "User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"
        }
        params = {"last_mask_id": 0}
        conn = sqlite3.connect("mp.db")
        cur = conn.cursor()
        cur.execute(
            """--sql
                create table if not exists article
                (
                    id            integer primary key autoincrement  not null,
                    user_id       integer                            not null,
                    mask_id       text unique                        not null,
                    title         text                               not null,
                    cover_img_url text                               not null,
                    create_time   integer                            not null,
                    is_down       integer check ( is_down in (0, 1)) not null
                );
            """
        )

        article_data = []

        while True:
            response = client.get(url=url, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"请求失败，状态码：{response.status_code}")
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析JSON数据")

            page_data = data.get("data", [])
            items = []
            for item in page_data:
                items.append(
                    (
                        user_id,
                        item.get("mask_id"),
                        item.get("title"),
                        item.get("cover_img_url"),
                        item.get("create_time"),
                        0,
                    )
                )
            article_data.extend(items)

            if not page_data or len(page_data) < 20:
                break

            if page_data:
                last_item = page_data[-1]
                params["last_mask_id"] = last_item.get("mask_id", 0)

        print(len(article_data))

        cur.executemany(
            """--sql
                insert into article (user_id, mask_id, title, cover_img_url, create_time, is_down)
                values (?, ?, ?, ?, ?, ?);
            """,
            article_data,
        )
        conn.commit()
        conn.close()
        print("数据已保存到数据库。")
        return


if __name__ == "__main__":
    main()
