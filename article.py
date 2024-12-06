from pprint import pprint
import time
import json
import httpx
import sqlite3


con = sqlite3.connect("meipian.db")
cur = con.cursor()
cur.execute(
    """
        create table if not exists article
        (
            user_id       integer                            not null,
            mask_id       text primary key                   not null,
            create_time   integer                            not null,
            url           text                               not null,
            title         text                               not null,
            cover_img_url text                               not null,
            is_down       integer default 0                  not null,
            check ( is_down in (0, 1)) 
        );
    """
)


def main():

    user_id = 4798939
    url = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
    headers = {
        "User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"
    }
    params = {"last_mask_id": 0}

    with httpx.Client() as client:
        while True:
            try:
                response = client.get(url=url, headers=headers, params=params)
                data = response.json()
                page = data["data"]
                items = [
                    {
                        "user_id": user_id,
                        "mask_id": item["mask_id"],
                        "create_time": item["create_time"],
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
                pprint("插入数据中----------------------------")
                params["last_mask_id"] = page[-1]["mask_id"]
                if not page or len(page) < 20:
                    break

            except httpx.HTTPStatusError as e:
                print(f"HTTP状态错误:{e}")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误:{e}")
            finally:
                pass
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
