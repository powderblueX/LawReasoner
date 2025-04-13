from dashscope import Generation
import json,re,os
from docx import Document 
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import gc
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

# 读取 txt 文件中的每一行内容
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 去除每行末尾的换行符和多余的空白字符
    lines = [os.path.splitext(line.strip())[0] for line in lines if line.strip()]
    return lines

# 为每一行分配 ID，并生成字典列表
def create_data_with_ids(lines):
    data_list = []
    for idx, line in enumerate(lines, start=1):  # 从 1 开始分配 ID
        data_list.append({
            "id": idx,
            "name": line
        })
    return data_list


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
    return []

def format_message(text,ph):
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'''请仔细分析文本，提取出与关键词相关的信息。如果文本中没有某个关键词对应的信息，则其值记为空字符串。请以JSON格式返回结果。

        文本内容：
        {text}

        需要提取的关键词：
        {ph}

        要求：
        1. 仔细阅读文本，找出与每个关键词相关的信息
        2. 如果文本中没有某个关键词的信息，则其值设为空字符串
        3. 直接返回JSON格式的结果，不要添加任何解释性文字

        示例：
        输入文本：我的手机号是13707031841，我们明天下午在公园集合。
        关键词：联系电话，时间，地点
        输出：
        {{
            "联系电话":"13707031841",
            "时间":"明天下午",
            "地点":"公园"
        }}'''}]
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
    print(f"从JSON文件加载的占位符: {ph}")
    ph = ','.join(ph)
    print(f"用户输入文本: {text}")
    print(f"需要提取的关键词: {ph}")

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
        print(f"模型返回的原始响应: {response_text}")
    else:
        print("API响应格式不正确")
    response_json = clean_json(response_text)
    print(f"解析后的JSON数据: {response_json}")
    return response_json

def extract_keywords(text):
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'''请仔细分析以下文本，提取出关键词，特别是合同类型相关的关键词。请直接输出关键词，用逗号分隔。

            要求：
            1. 重点关注合同类型相关的关键词（如买卖合同、租赁合同、服务合同等）
            2. 提取文本中提到的具体事项（如房屋、车辆、设备等）
            3. 提取文本中提到的金额、时间等关键信息
            4. 不要添加任何解释性文字

            文本内容：
            {text}

            示例：
            输入：我想买一辆二手车，价格在10万左右
            输出：二手车买卖合同,车辆买卖,10万,二手车'''}
        ]
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
        print(f"提取的关键词: {response_text}")
    else:
        print("API响应格式不正确")

    return clean_text(response_text)

def fill_template_to_bytes(template_docx, ph_json):
    # 把占位符对应的信息填入模版的占位符，并返回字节流
    print(f"开始填充模板，占位符数据: {ph_json}")
    
    # 首先收集所有需要替换的占位符
    all_placeholders = {f"{{{key}}}": value for key, value in ph_json.items()}
    print(f"所有需要替换的占位符: {all_placeholders}")
    
    # 遍历文档中的所有段落
    for paragraph in template_docx.paragraphs:
        # 先检查整个段落中是否包含占位符
        paragraph_text = paragraph.text
        if any(ph in paragraph_text for ph in all_placeholders.keys()):
            print(f"在段落中发现占位符: {paragraph_text}")
            
            # 保存原始格式
            original_style = paragraph.style
            
            # 清空原有runs
            paragraph.clear()
            
            # 按占位符分割文本
            parts = []
            current_text = paragraph_text
            
            # 找到所有占位符的位置
            placeholder_positions = []
            for ph in all_placeholders.keys():
                start = 0
                while True:
                    pos = current_text.find(ph, start)
                    if pos == -1:
                        break
                    placeholder_positions.append((pos, pos + len(ph), ph))
                    start = pos + len(ph)
            
            # 按位置排序
            placeholder_positions.sort()
            
            # 分割文本
            last_pos = 0
            for start, end, ph in placeholder_positions:
                if start > last_pos:
                    parts.append(current_text[last_pos:start])
                parts.append(all_placeholders[ph] if all_placeholders[ph] != "没有内容" else "    ")
                last_pos = end
            
            if last_pos < len(current_text):
                parts.append(current_text[last_pos:])
            
            # 添加新的runs
            for text in parts:
                run = paragraph.add_run(text)
                # 保持原有格式
                run.font.name = original_style.font.name
                run.font.size = original_style.font.size
    
    # 再次检查是否还有未替换的占位符
    for paragraph in template_docx.paragraphs:
        for run in paragraph.runs:
            if '{' in run.text and '}' in run.text:
                print(f"警告：发现未替换的占位符: {run.text}")
                
    template_docx = clean_contract(template_docx)
    return template_to_bytes(template_docx)

def template_to_bytes(template_docx):
    # 将文档保存到内存中的字节流
    byte_stream = BytesIO()
    template_docx.save(byte_stream)  # 将文档保存到字节流
    byte_stream.seek(0)  # 移动指针到字节流的开头

    return byte_stream

# 加载所有 .txt 文件的内容
def load_txt_files(folder_path):
    """
    从指定文件夹中加载所有 .txt 文件的内容。
    返回一个包含 (文件名, 文件内容) 的列表。
    """
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # 忽略空文件
                    documents.append((filename, content))
    return documents

def clean_text(text):
    """
    清理文本内容：
    - 去除多余空白字符（包括换行符、制表符等）。
    - 去除顿号、逗号等分隔符。
    - 去除特殊字符（如标点符号）。
    :param text: 原始文本
    :return: 清理后的文本
    """
    # 去除多余空白字符
    text = re.sub(r"\s+", " ", text).strip()
    
    # 去除顿号、逗号等分隔符
    text = re.sub(r"[、，,]", " ", text)
    
    # 去除其他特殊字符（可选）
    text = re.sub(r"[^\w\s]", "", text)
    
    return text.strip()

# 将文本内容向量化
def generate_embeddings(documents, model):
    """
    使用 SentenceTransformer 模型将文档内容转换为向量。
    返回文件名列表和对应的向量矩阵。
    """
    filenames, contents = zip(*documents)  # 分离文件名和内容
    # 清理内容
    contents = [clean_text(content) for content in contents]

    embeddings = model.encode(contents, convert_to_tensor=False)  # 生成向量
    return list(filenames), np.array(embeddings).astype('float32')

# 构建 FAISS 索引并保存
def build_faiss_index(embeddings, dimension):
    """
    使用 FAISS 构建向量索引。
    """
    index = faiss.IndexFlatL2(dimension)  # 使用 L2 距离
    index.add(embeddings)  # 添加向量到索引
    return index

# 加载 FAISS 索引
def load_faiss_index(index_file):
    """
    从磁盘加载 FAISS 索引。
    """
    index = faiss.read_index(index_file)
    print(f"FAISS 索引已加载，包含 {index.ntotal} 个向量")
    return index

# 查询知识库
def search_in_knowledge_base(query, model, index, filenames, top_k=5):
    """
    根据查询字符串在知识库中搜索最相似的文档。
    """
    query_vector = model.encode([query], convert_to_tensor=False).astype('float32')
    distances, indices = index.search(query_vector, top_k)
    results = [(filenames[i], distances[0][j]) for j, i in enumerate(indices[0])]
    return results

def format_template_keywords(docx_content):
    messages = [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': f'''请仔细分析以下合同模板内容，提取出能体现该合同独特性的关键词。请直接输出关键词，用逗号分隔。

要求：
1. 重点关注该合同特有的内容，不要提取通用条款（如违约责任、争议解决等）
2. 提取合同涉及的具体标的物（如具体型号的设备、特定位置的房屋等）
3. 提取合同特有的交易条件（如特殊的价格计算方式、独特的交付要求等）
4. 提取合同适用的特定场景（如特定行业、特殊用途等）
5. 提取合同中的特殊条款（如特殊的质量要求、特殊的验收标准等）
6. 不要提取通用性条款，如：技术标准、质量要求、交付期限、违约责任、争议解决、定金条款、留置权等
7. 不要添加任何解释性文字

合同模板内容：
{docx_content}

示例：
输入：[买卖合同模板内容]
输出：二手房交易,学区房,按揭贷款,房屋过户,税费承担,房屋现状'''}
    ]
    return messages

def extract_template_keywords(docx_content):
    """
    从合同模板中提取关键词
    """
    messages = format_template_keywords(docx_content)
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
        print(f"提取的模板关键词: {response_text}")
    else:
        print("API响应格式不正确")
    
    return response_text

def process_contract_templates(input_folder, output_folder):
    """
    处理合同模板文件夹中的所有docx文件，提取关键词并保存
    """
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 获取所有docx文件
    all_files = [f for f in os.listdir(input_folder) if f.endswith('.docx')]
    total_files = len(all_files)
    
    for index, file_name in enumerate(all_files, 1):
        try:
            print(f"正在处理文件: {file_name} 进度:{index}/{total_files}")
            
            # 读取docx文件
            file_path = os.path.join(input_folder, file_name)
            docx_content = get_docx(file_path)
            
            # 提取关键词
            keywords = extract_template_keywords(docx_content)
            
            # 保存到txt文件
            txt_path = os.path.join(output_folder, file_name.replace('.docx', '.txt'))
            save_string_to_txt(keywords, txt_path)
            
        except Exception as e:
            print(f"处理文件 {file_name} 时出错: {e}")
            continue

if __name__ == "__main__":
    input_folder = "contracts/地方"
    output_folder = "contracts/地方/关键词"
    process_contract_templates(input_folder, output_folder)




    