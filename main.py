import json
import httpx
import re

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
        # 获取输入的ID或URL
        user_id = get_input()
        # 构造请求URL
        url = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
        headers = {"User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"}
        params = {"last_mask_id": 0}

        article_data = []
        page = 0

        while True:

            response = client.get(url=url, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception(f"请求失败，状态码：{response.status_code}")
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析JSON数据")
            
            # 提取并处理当前页的数据
            page_data = data.get("data", [])
            article_data.extend(page_data)

            # 当数据不足20条或没有新数据时，停止循环
            if not page_data or len(page_data) < 20:
                break

            # 更新请求参数，以便下一次请求获取下一页数据
            if page_data:
                last_item = page_data[-1]
                params["last_mask_id"] = last_item.get("mask_id", 0)
                
            page += 1
            print(f"第{page}页数据获取成功，获取到{len(page_data)}条数据")

    # 输出最终获取到的数据量和数据列表
    print(f"共获取到{len(article_data)}条数据")
    print(article_data)
    


if __name__ == "__main__":
    main()