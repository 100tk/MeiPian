import json
import httpx
import sqlite3
from datetime import datetime


def main():
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

        user_id = 59224950
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
                    print(f"HTTP状态错误:{e}")
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误:{e}")
                except sqlite3.Error as e:
                    print(e)
    finally:
        con.close()


if __name__ == "__main__":
    main()
