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
                if not page or len(page) > 20:
                    break
                params["last_mask_id"] = page[-1]["mask_id"]
            except httpx.HTTPStatusError():
                break
            except json.JSONDecodeError():
                break
            finally:
                time.sleep(0.5)


if __name__ == "__main__":
    pass
