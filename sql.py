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
