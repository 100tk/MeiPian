import sqlite3

def init_database():
    # 创建SQLite数据库连接
    conn = sqlite3.connect('meipian_data.db')
    cursor = conn.cursor()
    
    # 创建数据表，用于存储文章数据
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        -- 可以在这里添加其他字段，如发布时间、点赞数等
        -- ...
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建数据表，用于存储爬取状态信息
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS crawl_status (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        last_mask_id INTEGER NOT NULL,
        page_number INTEGER NOT NULL,
        last_crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print("数据库初始化完成")




def main():
    init_database()
    
    # 连接到SQLite数据库
    conn = sqlite3.connect('meipian_data.db')
    cursor = conn.cursor()
    
    # 获取输入的ID或URL
    user_id = get_input()
    
    # 检查数据库中是否存在爬取状态记录
    cursor.execute("SELECT last_mask_id, page_number FROM crawl_status WHERE user_id=?", (user_id,))
    status_result = cursor.fetchone()
    
    if status_result:
        # 如果存在记录，则恢复状态
        last_mask_id, page_number = status_result
        params = {"last_mask_id": last_mask_id}
        print(f"从断点续爬，上次爬取到mask_id为{last_mask_id}，页码为{page_number}")
    else:
        # 如果不存在记录，则开始新的爬取
        params = {"last_mask_id": 0}
        page_number = 1
    
    # 构造请求URL和其他代码保持不变...
    
    # 循环爬取数据
    while True:
        # ...（发送请求、解析响应、提取和处理数据的代码保持不变）
        
        # 更新爬取状态
        cursor.execute("REPLACE INTO crawl_status (user_id, last_mask_id, page_number) VALUES (?, ?, ?)",
                        (user_id, last_item.get("mask_id", 0) if page_data else 0, page_number))
        conn.commit()
        
        # 检查是否还有更多数据需要爬取
        if not page_data or len(page_data) < 20:
            break
        
        # ...（更新请求参数、打印信息、增加页码的代码保持不变）
    
    # 关闭数据库连接
    conn.close()
    
    # ...（输出最终获取到的数据量和数据列表的代码保持不变）

# 如果这是主模块，则运行main函数
if __name__ == "__main__":
    main()
