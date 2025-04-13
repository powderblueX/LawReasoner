from dashscope import Generation
import json,re
from docx import Document 
from docx.enum.text import WD_ALIGN_PARAGRAPH

def load_json(file_path):
    """
    从指定路径加载 JSON 文件并返回其内容。
    
    :param file_path: JSON 文件路径
    :return: 加载的 JSON 数据（列表）
    """
    try:
        # 打开 JSON 文件并加载内容
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f) 
        return data["placeholders"] # 一个列表
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到！")
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是有效的 JSON 格式！")
    except Exception as e:
        print(f"发生未知错误：{e}")

def format_message(text,ph):
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'''请直接输出提取到的关键信息，不要添加任何解释性文字或额外说明，任务：依据我给你的关键词和文本，去提取文本中关键词对应的信息,以json格式返回
            输入示例：
            我的手机号是13707031841，我们明天下午在公园集合。关键词：联系电话，时间，地点
            输出示例：
            {{
                "联系电话":"13707031841",
                "时间":"明天下午",
                "地点":"公园"
            }}
            以下是我给出的文本：
            {text}
            以下是关键词：
            {ph}'''}]
    return messages

def clean_json(raw_json):
    """
    清洗大模型输出的 JSON 数据，移除开头的 ```json 和结尾的 ```。
    :param raw_json: 原始的 JSON 字符串（可能包含多余符号）
    :return: 清洗后的 JSON 数据（Python 字典格式）
    """
    try:
        # 1. 去除开头的 ```json 和结尾的 ```
        cleaned_data = raw_json.strip()
        if cleaned_data.startswith("```json"):
            cleaned_data = cleaned_data[len("```json"):].strip()
        if cleaned_data.endswith("```"):
            cleaned_data = cleaned_data[:-3].strip()

        # 2. 将清洗后的字符串解析为 JSON
        parsed_json = json.loads(cleaned_data)
        
        return parsed_json

    except json.JSONDecodeError as e:
        print(f"JSON 解码失败: {e}")
        return None

def clean_contract(docx):
    for paragraph in docx.paragraphs:
        # 使用正则表达式匹配大括号及其中的内容，并替换为空字符串
        for run in paragraph.runs:
            run.text = re.sub(r'\{.*?\}', '', run.text)
        # 设置段落对齐方式为向左对齐
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    return docx
def extract_ph(text,ph_json):
    # 从text中提取占位符对应的信息
    #return json格式
    ph = load_json(ph_json)
    ph = ','.join(ph)

    messages = format_message(text, ph)
    # 调用API生成响应
    response = Generation.call(
        api_key="sk-4c0e21d21fb748bd81d918e0cdc346f3",
        model="qwen-turbo",
        messages=messages,
        result_format="message"
    )
    
    response_text = ""
    if hasattr(response, 'output') and hasattr(response.output, 'choices'):
        # 获取处理后的结果
        response_text = response['output']['choices'][0]['message']['content']
    else:
        print("API响应格式不正确")
    response_json = clean_json(response_text)
    return response_json

def fill_template(template_docx,ph_json,output_path):
    # 把占位符对应的信息填入模版的占位符
    # return最终合同
    for paragraph in template_docx.paragraphs:
        for run in paragraph.runs:
            for key, value in ph_json.items():
                ph = f"{{{key}}}"
                if ph in paragraph.text:
                    # 替换段落中的占位符
                    if value != '':
                        paragraph.text = paragraph.text.replace(ph, str(value))
                    else:
                        paragraph.text = paragraph.text.replace(ph, "待填写")
                
    template_docx = clean_contract(template_docx)
    template_docx.save(output_path)
    print(f"已保存至{output_path}")
    return 
# 示例调用
if __name__ == "__main__":
    with open("str1.txt", 'r', encoding='utf-8') as file:
        text = file.read()
    ph_json = extract_ph(text,"contracts/tran_template/部委模版/占位符/保管合同　GF—2000—0801.json")
    docx = Document("contracts/tran_template/部委模版/保管合同　GF—2000—0801.docx")
    output_path = "./testContract.docx"

    fill_template(docx,ph_json,output_path)

    