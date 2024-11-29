import json
import httpx
import time

from typing import Dict, Any, List


def main():

    user_id: int = 36679026
    url: str = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
    headers: dict[str, str] = {
        "User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"
    }
    params: dict[str, int] = {"last_mask_id": 0}

    with httpx.Client() as client:
        while True:
            response: httpx.Response = client.get(
                url=url, headers=headers, params=params
            )
            if response.status_code != 200:
                raise Exception(f"请求失败")
            try:
                data: Dict[str, List[Dict[str, Any]]] = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析响应数据")

            page: List[Dict[str, any]] = data["data"]

            items: list[dict[str, str]] = [
                {
                    "user_id": user_id,
                    "mask_id": item["mask_id"],
                    "create_time": item["create_time"],
                    "title": item["title"].replace(" ", ""),
                    "url": f"https://www.meipian.cn/{item['mask_id']}",
                    "cover_img_url": item["cover_img_url"],
                }
                for item in page
            ]
            print(items)

            params["last_mask_id"] = page[-1]["mask_id"]
            if not page or len(page) < 20:
                break


if __name__ == "__main__":
    main()
