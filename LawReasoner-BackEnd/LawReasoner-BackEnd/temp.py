from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch,re
from flask import Flask, request, jsonify
from flask_cors import CORS
import markdown
import atexit

# 设置模型路径
model_path = "model-7B"
env = "cuda"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16).to(env)  # 使用半精度浮点数并加载到GPU

# 如果存在generation config，则加载它
try:
    generation_config = GenerationConfig.from_pretrained(model_path)
except Exception as e:
    print("No generation config found or error occurred:", e)
    generation_config = None

    
app = Flask(__name__)
# 允许所有来源的CORS请求。对于生产环境，请指定具体的域名。
CORS(app)

#修正缩行问题
def fix_indentation(markdown_text):
    """
    将Markdown文本中每行前缀为3个空格的行改为4个空格。
    """
    lines = markdown_text.split('\n')
    corrected_lines = []
    
    for line in lines:
        if line.startswith('   '):  # 检查是否以3个空格开始
            # 替换3个空格为4个空格
            corrected_line = '    ' + line[3:]
        else:
            corrected_line = line
        corrected_lines.append(corrected_line)
    
    return '\n'.join(corrected_lines)


legal_keywords = [
        "法律", "法规", "案件", "合同", "诉讼", "仲裁", "法庭", "律师","法院",
        "证据", "判决", "侵权", "赔偿", "刑事责任", "民事责任", "刑法", "民法",
        "诉称", "辩称", "原告", "被告"
    ]
def is_legal_related(input_text):
    # 检查输入是否包含法律相关关键词
    for keyword in legal_keywords:
        if re.search(rf"\b{keyword}\b", input_text, re.IGNORECASE):
            return True
    return False


#测试
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"answer": "成功连接到后端!"})

#模型服务
@app.route('/deepseek', methods=['POST'])
def deepseek():
    # 输入
    input_json = request.get_json()
    query = input_json['message']
    
    '''if not is_legal_related(query):
        answer = "请输入法律相关问题"
        # 构建响应JSON
        response_data = {
            "answer": answer,
            "status": "success"
        }

        # 返回JSON响应
        return jsonify(response_data)'''
    
    query = f"""
        你是一个中文法律助手，任务是根据提供的案例信息生成结构化的摘要。请严格按照以下格式组织你的回答，并确保所有关键信息都被包含在方括号内。

        以下是用户提供的案例信息：
        [用户提供的具体案例内容]

        请按照以下格式改写上述案例信息，并确保所有关键信息都被放置在方括号内：
        1. **识别关键信息**
           - 原告：[原告名称]
             控告内容：[具体的控告内容]
           - 被告：[被告名称]
             辩称情况：[具体的辩称情况]

        2. **适用法律依据**
           - [相关法律条文或法规]

        3. **推理步骤**
           - **Step 1**: [请在此处填写分析1的具体内容]
             证据: [支持分析1的证据]
           - **Step 2**: [请在此处填写分析2的具体内容]
             证据: [支持分析2的证据]
           - **Step 3**: [请在此处填写分析3的具体内容]
             证据: [支持分析3的证据]
           - **Step 4**: [请在此处填写分析4的具体内容]
             证据: [支持分析4的证据]

        4. **结论**
           [法院可能采取的具体判决内容]

        现在，请根据以下用户查询改写成所需的格式：
        以下是一篇法律文书：{query}"""
    
    
    # 将输入编码，并将其移动到GPU
    inputs = tokenizer(query, return_tensors="pt").to(env)
    # 打印输入文本的长度（以token计数）
    print(f"Input length: {len(inputs[0])}")
    
    # 使用特定的生成配置进行预测（如果有的话）
    outputs = model.generate(inputs['input_ids'], generation_config=generation_config)

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(answer)
    
    end_tag_position = answer.find('</think>')
    if end_tag_position != -1:
        # 裁剪字符串，保留</think>标签之后的内容
        answer = answer[end_tag_position + len("</think>"):]
    answer = fix_indentation(answer)
    answer = markdown.markdown(answer)
    
    # 构建响应JSON
    response_data = {
        "answer": answer,
        "status": "success"
    }

    # 返回JSON响应
    return jsonify(response_data)


def cleanup():
    """释放显存"""
    global model
    del model
    torch.cuda.empty_cache()

# 注册cleanup函数为退出时执行的函数
atexit.register(cleanup)

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        # 在finally块中也调用cleanup以确保资源释放
        cleanup()
#import gc

# 执行完模型相关的操作后
#model = None
#torch.cuda.empty_cache()
#gc.collect()
