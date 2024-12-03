from typing import Dict, List, Any, AnyStr

import time
import json
import httpx


def main():

    user_id: int = 36679026
    url: str = f"https://www.meipian.cn/service/user/{user_id}/article/open-list"
    headers: Dict[str, str] = {
        "User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"
    }
    params: Dict[str, int] = {"last_mask_id": 0}

    with httpx.Client() as client:
        while True:
            try:
                response: httpx.Response = client.get(
                    url=url, headers=headers, params=params
                )
                data: Dict[str, List[Dict[str, str]]] = response.json()
                page: List[Dict[str, str]] = data["data"]
                items: List[Dict[str, str]] = [
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
                # 保存数据到文件
                with open(f"article_{user_id}.json", "a", encoding="utf-8") as f:
                    f.write(json.dumps(items, ensure_ascii=False) + "\n")

                params["last_mask_id"] = page[-1]["mask_id"]
                if not page or len(page) < 20:
                    break

            except httpx.HTTPStatusError():
                break
            except json.JSONDecodeError():
                break
            finally:
                time.sleep(0.5)


if __name__ == "__main__":
    main()
