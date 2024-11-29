import json
import sqlite3
import httpx
import re

from typing import Any, Dict,List

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


conn = sqlite3.connect("mp.db")
cursor = conn.cursor()
cursor.execute(
    """--sql
            create table if not exists article
            (
                id            integer primary key autoincrement  not null,
                mask_id       text unique                        not null,
                title         text                               not null,
                cover_img_url text                               not null,
                create_time   integer                            not null,
                is_down       integer default 0                  not null,
                create_data   default current_date               not null,
                check ( is_down in (0, 1)) 
            );
"""
)


def main() -> None:

    with httpx.Client() as client:

        user_id = get_input()

        url = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
        headers = {
            "User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"
        }
        params = {"last_mask_id": 0}

        while True:

            # 发送请求
            response = client.get(url=url, headers=headers, params=params)

            # 检查响应状态码
            if response.status_code != 200:
                raise Exception(f"请求失败，状态码：{response.status_code}")

            # 解析响应
            try:
                data:Dict[str, Any] = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析JSON数据")

            # 提取并处理当前页的数据
            page_data:List[Dict[str, str]] = data.get("data", [])

            # 使用列表推导式组合新字典
            items:list[dict[str,str]] = [
                {
                    'user_id':user_id,
                    'mask_id':item['mask_id'],
                    'title':item['title'].replace(' ',''),
                    'cover_img_url':item['cover_img_url'],
                    'create_time':item['create_time']
                    
                }
                for item in page_data
            ]

            # 批量插入数据库
            cursor.executemany(
                """--sql
                        INSERT INTO article (mask_id,title,cover_img_url,create_time)
                        VALUES (:mask_id,:title,:cover_img_url,:create_time)
                """,
                items
            )
            print('插入数据中------------------------------------------') 
            


            # 更新请求参数，以便下一次请求获取下一页数据
            params["last_mask_id"] = page_data[-1]["mask_id"]
            # 当数据不足20条或没有新数据时，停止循环
            if not page_data or len(page_data) < 20:
                break
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
