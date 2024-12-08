import httpx
import asyncio

from rich.progress import Progress, TextColumn, BarColumn, DownloadColumn


async def download(urls):
    """
    异步下载多个图片文件。

    :param urls: 一个包含 (img_url, filename) 元组的列表，其中 img_url 是图片的 URL，filename 是保存的文件名。
    :return: None
    """

    async def download_img(img_url, filename, progress):
        """
        异步下载单个图片文件并显示进度。

        :param img_url: 图片的 URL。
        :param filename: 保存的文件名。
        :param progress: 进度条对象，用于显示下载进度。
        :return: None
        """
        try:
            # 创建异步 HTTP 客户端
            async with httpx.AsyncClient() as client:
                # 发起 GET 请求并流式处理响应
                async with client.stream("GET", img_url) as response:
                    response: httpx.Response
                    total = int(response.headers.get("content-length"))  # 获取文件总大小
                    task_id = progress.add_task(description=f"下载图片:{filename}", total=total)  # 添加任务到进度条
                    with open(filename, "wb") as file:
                        # 逐块读取响应内容并写入文件
                        async for chunk in response.aiter_bytes(chunk_size=1024):
                            file.write(chunk)
                            progress.update(task_id, advance=len(chunk))  # 更新进度条
        except Exception as e:
            print(e)  # 打印异常信息

    # 创建进度条对象
    with Progress(TextColumn("[bold blue][progress.description]{task.description}"), BarColumn(), DownloadColumn()) as progress:
        tasks = [download_img(img_url, filename, progress) for img_url, filename in urls]  # 生成下载任务列表
        await asyncio.gather(*tasks)  # 并发执行所有下载任务



if __name__ == "__main__":
    urls = [
        (
            "https://ss-mpvolc.meipian.me/users/36679026/5fbbf86d979e3e9ea764d9d9a2c09dca__jpg.heic~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg",
            "1.jpg",
        ),
        (
            "https://ss-mpvolc.meipian.me/users/36679026/ec3508cbd4b32dc2bf0ca7d82883bfca__jpg.heic~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg",
            "2.jpg",
        ),
        (
            "https://ss-mpvolc.meipian.me/users/36679026/5ee2d5fdbfd1f40537a3a3b2bd7cd6fa__jpg.heic~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg",
            "3.jpg",
        ),
        (
            "https://ss-mpvolc.meipian.me/users/36679026/0522a03a1c65d59b00148d87086d2e62__jpg.heic~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg",
            "4.jpg",
        ),
        (
            "https://ss-mpvolc.meipian.me/users/36679026/becfb972b7a6e15203299246bd52c4ae__jpg.heic~tplv-s1ctq42ewb-s3-cC-q:5000:0:0:0:q100.jpg",
            "5.jpg",
        ),
    ]
    asyncio.run(download(urls))
