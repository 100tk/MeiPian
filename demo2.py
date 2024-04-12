import json
import httpx
import re
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """Create a database connection to the SQLite database specified by db_file."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")
    except Error as e:
        print(f"Error connecting to SQLite database: {e}")
    return conn


def create_table(conn, create_table_sql):
    """Create a table from the create_table_sql statement."""
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
    except Error as e:
        print(f"Error creating table: {e}")


def insert_article(conn, article):
    """Insert a single article into the articles table."""
    sql = """
        INSERT INTO articles (user_id, mask_id, title, cover, views, likes, comments, shares, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor = conn.cursor()
    cursor.execute(sql, article)
    conn.commit()
    print(f"Inserted article with mask_id: {article[1]}")


def get_last_mask_id(conn, user_id):
    """Get the last mask_id stored for the given user_id."""
    sql = "SELECT MAX(mask_id) FROM articles WHERE user_id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


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
    db_file = "meipian_articles.db"
    conn = create_connection(db_file)

    # Create the articles table if it doesn't exist
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            mask_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            cover TEXT NOT NULL,
            views INTEGER NOT NULL,
            likes INTEGER NOT NULL,
            comments INTEGER NOT NULL,
            shares INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
    """
    create_table(conn, create_table_sql)

    with httpx.Client() as client:

        # 获取输入的ID或URL
        user_id = get_input()

        # 获取上次爬取的最后一条记录的mask_id（断点续爬）
        last_mask_id = get_last_mask_id(conn, user_id)
        if last_mask_id:
            params = {"last_mask_id": last_mask_id}
        else:
            params = {"last_mask_id": 0}

        article_data = []
        page = 0

        while True:
            # 发送请求
            response = client.get(
                url=f"https://www.meipian.cn/service/user/{user_id}/article/open-list",
                headers={"User-Agent": "Opera/9.80 ..."},  # (保留原有User-Agent)
                params=params,
            )

            # 检查响应状态码
            if response.status_code != 200:
                raise Exception(f"请求失败，状态码：{response.status_code}")

            # 解析响应
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析JSON数据")

            # 提取并处理当前页的数据
            page_data = data.get("data", [])

            # 将当前页的数据插入到数据库中
            for article in page_data:
                insert_article(conn, (
                    user_id,
                    article.get("mask_id"),
                    article.get("title"),
                    article.get("cover"),
                    article.get("views"),
                    article.get("likes"),
                    article.get("comments"),
                    article.get("shares"),
                    article.get("created_at"),
                ))

            # 当数据不足20条或没有新数据时，停止循环
            if not page_data or len(page_data) < 20:
                break

            # 更新请求参数，以便下一次请求获取下一页数据
            if page_data:
                last_item = page_data[-1]
                params["last_mask_id"] = last_item.get("mask_id", 0)

            page += 1
            print(f"第{page}页数据获取成功，获取到{len(page_data)}条数据")

    # 关闭数据库连接
    conn.close()

    # 输出最终获取到的数据量
    print(f"共获取到{len(page_data)}条数据（已存储到数据库）")


if __name__ == "__main__":
    main()
