import json
import httpx

from typing import Dict, Any, List

def main():
    url: str = "https://www.meipian.cn/service/user/36679026/article/open-list"
    headers: dict[str, str] = {"User-Agent": "Opera/9.80 (iPhone; Opera Mini/8.0.0/34.2336; U; en) Presto/2.8.119 Version/11.10"}
    params: dict[str, int] = {"last_mask_id": 0}

    with httpx.Client() as client:
        while True:
            response: httpx.Response = client.get(url=url, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"请求失败")
            try:
                data: Dict[str, List[Dict[str, Any]]] = response.json()
            except json.JSONDecodeError:
                raise Exception("无法解析响应数据")

            page: List[Dict[str, Any]] = data['data']
            for item in page:
                del item['abstract']


            if not page or len(page) < 20:
                break
            params["last_mask_id"] = page[-1]["mask_id"]


if __name__ == '__main__':
    main()