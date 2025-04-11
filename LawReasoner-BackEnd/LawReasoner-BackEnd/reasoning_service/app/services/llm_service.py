import httpx
import asyncio
from typing import AsyncGenerator
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch
import re
import markdown
from fastapi import HTTPException
import atexit
import os
from app.core.config import settings
import json

# 配置日志
logger = logging.getLogger("llm_service")
logger.setLevel(logging.INFO)

class LLMService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 单例模式，避免重复初始化
        if self._initialized:
            return
        
        logger.info("初始化大模型服务...")
        
        # 如果设置为使用本地模型，则加载本地模型
        if settings.USE_LOCAL_MODEL:
            try:
                self._init_local_model()
            except Exception as e:
                logger.error(f"加载本地模型失败: {str(e)}")
                self.model = None
                self.tokenizer = None
        else:
            self.model = None
            self.tokenizer = None
            
        LLMService._initialized = True
    
    def _init_local_model(self):
        """初始化本地模型"""
        logger.info(f"正在加载本地模型: {settings.LOCAL_MODEL_PATH}")
        
        model_path = settings.LOCAL_MODEL_PATH
        env = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, 
            torch_dtype=torch.float16 if env == "cuda" else torch.float32
        ).to(env)
        
        # 如果存在generation config，则加载它
        try:
            self.generation_config = GenerationConfig.from_pretrained(model_path)
        except Exception as e:
            logger.warning(f"未找到生成配置或发生错误: {e}")
            self.generation_config = None
            
        logger.info(f"本地模型加载成功，运行环境: {env}")
    
    def _fix_indentation(self, markdown_text):
        """修正缩进问题"""
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
    
    def _prepare_prompt(self, user_input):
        """准备发送给模型的提示"""
        # 这里根据模型的需要可以调整提示的格式
        prompt = f"""
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
        以下是一篇法律文书：{user_input}"""
        
        return prompt
    
    async def generate_local(self, user_input) -> str:
        """使用本地模型生成回复"""
        if not self.model or not self.tokenizer:
            raise HTTPException(status_code=500, detail="本地模型未正确加载")
        
        prompt = self._prepare_prompt(user_input)
        
        # 将输入编码，并将其移动到合适的设备
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        logger.info(f"输入长度: {len(inputs['input_ids'][0])}")
        
        # 使用特定的生成配置进行预测（如果有的话）
        outputs = self.model.generate(
            inputs['input_ids'], 
            generation_config=self.generation_config
        )
        
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # 后处理
        end_tag_position = answer.find('</think>')
        if end_tag_position != -1:
            # 裁剪字符串，保留</think>标签之后的内容
            answer = answer[end_tag_position + len("</think>"):]
            
        answer = self._fix_indentation(answer)
        answer = markdown.markdown(answer)
        
        return answer
    
    async def generate_remote(self, user_input: str, url: str = None) -> str:
        """向远程模型服务发送请求并获取回复"""
        # 如果没有提供URL，使用配置中的URL
        if url is None:
            url = settings.REMOTE_MODEL_URL
        
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"向远程模型发送请求: {url}")
                
                # 打印请求内容，帮助调试
                request_data = {"message": user_input}
                logger.info(f"请求数据: {request_data}")
                
                response = await client.post(
                    url,
                    json=request_data,
                    timeout=60.0,  # 设置较长的超时时间
                    headers={"Content-Type": "application/json"}
                )
                
                # 记录响应状态和内容
                logger.info(f"远程API响应状态码: {response.status_code}")
                logger.info(f"远程API响应头: {response.headers}")
                
                # 尝试记录响应内容
                try:
                    response_text = response.text
                    logger.info(f"远程API响应内容: {response_text[:200]}...")
                except Exception as e:
                    logger.error(f"无法读取响应内容: {e}")
                
                # 检查HTTP状态码
                response.raise_for_status()
                
                # 尝试解析JSON响应
                try:
                    result = response.json()
                    # 尝试不同的响应字段
                    if "answer" in result:
                        return result["answer"]
                    elif "response" in result:
                        return result["response"]
                    elif "text" in result:
                        return result["text"]
                    elif "content" in result:
                        return result["content"]
                    elif "result" in result:
                        return result["result"]
                    else:
                        # 如果找不到已知格式，返回整个响应以便调试
                        logger.warning(f"未知的响应格式: {result}")
                        return f"模型返回了未知格式的响应: {str(result)[:200]}..."
                except Exception as parse_error:
                    logger.error(f"解析JSON响应时出错: {parse_error}")
                    # 如果不是JSON，返回原始文本
                    return f"模型返回了非JSON格式: {response.text[:200]}..."
                
            except httpx.HTTPStatusError as e:
                logger.error(f"远程API返回HTTP错误: {e.response.status_code} - {e.response.text}", exc_info=True)
                raise Exception(f"模型服务返回错误: HTTP {e.response.status_code}")
            except httpx.RequestError as e:
                logger.error(f"请求远程模型时发生错误: {e}", exc_info=True)
                raise Exception(f"无法连接到语言模型服务: {str(e)}")
            except Exception as e:
                logger.error(f"处理远程模型响应时发生错误: {e}", exc_info=True)
                raise Exception(f"模型响应处理失败: {str(e)}")
    
    async def generate_response(self, user_input: str) -> str:
        """根据配置生成回复"""
        try:
            if settings.USE_LOCAL_MODEL and self.model:
                logger.info("使用本地模型生成回复")
                return await self.generate_local(user_input)
            else:
                logger.info("使用远程模型生成回复")
                
                # 首先尝试主URL
                try:
                    logger.info(f"尝试主URL: {settings.REMOTE_MODEL_URL}")
                    return await self.generate_remote(user_input, settings.REMOTE_MODEL_URL)
                except Exception as primary_error:
                    logger.error(f"主URL失败: {str(primary_error)}")
                    
                    # 如果主URL失败，依次尝试备用URL
                    for i, fallback_url in enumerate(settings.REMOTE_MODEL_FALLBACK_URLS):
                        try:
                            logger.info(f"尝试备用URL {i+1}: {fallback_url}")
                            return await self.generate_remote(user_input, fallback_url)
                        except Exception as fallback_error:
                            logger.error(f"备用URL {i+1} 失败: {str(fallback_error)}")
                            continue
                    
                    # 如果所有URL都失败，抛出最初的错误
                    raise primary_error
        except Exception as e:
            # 记录详细错误信息
            logger.error(f"生成回复时发生未预期的错误: {str(e)}", exc_info=True)
            # 将异常向上传递，让调用者处理
            raise Exception(f"生成回复失败: {str(e)}")
    
    async def generate_stream_response(self, user_input: str) -> AsyncGenerator[str, None]:
        """生成流式回复"""
        try:
            # 本地模型和远程模型的处理方式不同
            if settings.USE_LOCAL_MODEL and self.model:
                # 本地模型的流式生成实现
                prompt = self._prepare_prompt(user_input)
                
                # 准备输入
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
                
                # 创建一个简单的流式生成配置（如果有）
                config = self.generation_config if self.generation_config else None
                
                # 使用本地模型流式生成
                # 注：这里模拟流式输出，真正的流式应根据模型能力实现
                full_response = ""
                
                # 使用模型生成，但做字符级流式处理
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs['input_ids'],
                        generation_config=config,
                        max_new_tokens=800,  # 合理限制生成长度
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                    
                    # 解码生成的文本
                    full_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    
                    # 移除prompt部分获取回复
                    if prompt in full_text:
                        response = full_text[len(prompt):]
                    else:
                        response = full_text
                    
                    # 清理和格式化响应
                    response = response.strip()
                    
                    # 模拟字符流式输出
                    for i in range(0, len(response), 3):  # 每次发送3个字符
                        chunk = response[i:i+3]
                        yield chunk
                        await asyncio.sleep(0.01)  # 小延迟
            else:
                # 远程模型的流式生成
                async with httpx.AsyncClient() as client:
                    # 发送请求到流式API
                    async with client.stream(
                        'POST',
                        f"{settings.REMOTE_MODEL_URL}/stream",
                        json={"message": user_input},
                        timeout=60.0
                    ) as response:
                        async for chunk in response.aiter_text():
                            # 处理来自远程API的SSE格式响应
                            if chunk.strip():
                                # 提取实际内容，假设远程API返回JSON
                                try:
                                    # 尝试解析JSON
                                    data = json.loads(chunk)
                                    text_chunk = data.get("text", "")
                                    if text_chunk:
                                        yield text_chunk
                                except json.JSONDecodeError:
                                    # 如果不是JSON，直接返回
                                    yield chunk.strip()
                                
                                await asyncio.sleep(0.01)  # 确保流畅输出
        except Exception as e:
            logger.error(f"流式生成回复时发生错误: {str(e)}")
            error_msg = f"服务暂时不可用，请稍后再试。(错误: {str(e)[:100]})"
            yield error_msg
    
    def cleanup(self):
        """释放资源"""
        if hasattr(self, 'model') and self.model:
            del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("已释放模型资源")

# 创建单例实例
llm_service = LLMService()

# 注册退出时的清理函数
atexit.register(llm_service.cleanup) 