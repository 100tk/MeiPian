

import re
import json
from bs4 import BeautifulSoup

# 假设html_content包含你的HTML内容
html_content = """
<html>
<head>
    <title>Test Page</title>
    <script>
        // 全局变量
        window.BLADE_ARTICLE_JSON = {
            name: "Example",
            age: 30,
            details: {
                address: "123 Street"
            }
        };
    </script>
    <!-- 其他script标签 -->
</head>
<body>
    <!-- 页面内容 -->
</body>
</html>
"""

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 查找所有的script标签
scripts = soup.find_all('script')

# 用于存储提取的JavaScript对象
extracted_objects = {}

# 遍历所有的script标签
for script in scripts:
    # 提取script标签的内容
    script_content = script.string
    if script_content:
        # 使用正则表达式查找可能的JavaScript对象定义
        # 注意：这只是一个简单的示例，实际的正则表达式可能需要更复杂的匹配逻辑
        object_definitions = re.findall(r'window.BLADE_ARTICLE_JSON\s*=\s*({.*?};)', script_content)
        
        for obj_name, obj_def in object_definitions:
            # 移除JavaScript对象定义中的变量名和等号
            cleaned_obj_def = obj_def.strip()
            
            # 尝试修复无引号的键，这里使用简单的replace，实际可能更复杂
            fixed_obj_def = re.sub(r'(\w+):', r'"\1":', cleaned_obj_def)
            
            try:
                # 尝试将修复后的字符串转换为Python字典
                extracted_object = json.loads(fixed_obj_def)
                # 将提取的对象存储到字典中，键为JavaScript对象的名称
                extracted_objects[obj_name] = extracted_object
            except json.JSONDecodeError as e:
                print(f"Error decoding object {obj_name}: {e}")

# 打印提取的对象
for obj_name, obj_value in extracted_objects.items():
    print(f"Object {obj_name}:")
    print(json.dumps(obj_value, indent=4))