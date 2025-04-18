from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form,Response
import  json,os
from app.services.contract import *
from app.core.config import settings
from pathlib import Path
from pydantic import BaseModel
from urllib.parse import quote
from typing import List, Dict, Any
import gc
import asyncio

api_router = APIRouter()
class ContractRequest(BaseModel):
    user_input: str
    template_id: int
    type: str

class RecommendRequest(BaseModel):
    user_input: str
    type: str

# 添加标准响应模型
class StandardResponse(BaseModel):
    code: int = 200
    message: str = "操作成功"
    data: Any = None

GLOBAL_MODEL = None
# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BASE_FILE_URL = "http://47.117.153.17/files"

@api_router.get("/contract/getAllName", response_model=StandardResponse)
async def get_all_contract_name(type:str):
    try:
        lines = read_txt_file(os.path.join(BASE_DIR,"contracts","RAG",type,"filenames.txt"))
        data_list = create_data_with_ids(lines)
        
        # 返回标准响应格式
        return StandardResponse(
            code=200,
            message="获取合同列表成功",
            data=data_list
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"获取合同列表失败: {str(e)}",
            data=[]
        )

    
@api_router.get("/contract/getContractNameById", response_model=StandardResponse)
async def get_contract_name_by_id(id:int,type:str):
    try:
        files = await get_all_contract_name(type)
        if isinstance(files, StandardResponse):
            files = files.data
        file = next((item for item in files if item['id'] == id), None)
        if file is None:
            return StandardResponse(
                code=404,
                message=f"未找到 ID 为 {id} 的合同",
                data=None
            )
        return StandardResponse(
            code=200,
            message="获取合同名称成功",
            data=file['name']
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"获取合同名称失败: {str(e)}",
            data=None
        )

@api_router.get("/contract/getContractIdByName", response_model=StandardResponse)
async def get_contract_id_by_name(name:str,type:str):
    try:
        files = await get_all_contract_name(type)
        if isinstance(files, StandardResponse):
            files = files.data
        file = next((item for item in files if item['name'] == name), None)
        if file is None:
            return StandardResponse(
                code=404,
                message=f"未找到名称为 {name} 的合同",
                data=None
            )
        return StandardResponse(
            code=200,
            message="获取合同 ID 成功",
            data=file['id']
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"获取合同 ID 失败: {str(e)}",
            data=None
        )

@api_router.post("/contract/generateContract", response_model=StandardResponse)
async def generate_contract(request: ContractRequest):
    try:
        # 获取合同名称
        name_response = await get_contract_name_by_id(request.template_id, request.type)
        contract_name = name_response.data if isinstance(name_response, StandardResponse) else name_response
        
        # 定义部委模板和地方模板的占位符文件路径
        ph_path = os.path.join(BASE_DIR,"contracts","tran_template",f"{request.type}模版","占位符",f"{contract_name}.json")
        docx_path = os.path.join(BASE_DIR,"contracts","tran_template",f"{request.type}模版",f"{contract_name}.docx")
        
        # 检查ph是否存在
        if os.path.exists(ph_path):
            ph_json = extract_ph(request.user_input, ph_path)
        else:
            raise FileNotFoundError(f"未找到占位符文件：{contract_name}.docx")

        # 检查模板是否存在
        if os.path.exists(docx_path):
            docx = Document(docx_path)
        else:
            raise FileNotFoundError(f"未找到合同模板文件：{contract_name}.docx")

        # 填充模板
        filled_docx = fill_template(docx, ph_json)
        
        # 生成唯一文件名 - 以生成的时间戳为前缀，保持原文件名
        import datetime
        import uuid
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_contract_name = f"generated_{timestamp}_{unique_id}_{contract_name}"
        file_name = f"{new_contract_name}.docx"
        
        # 创建保存目录
        save_dir = os.path.join(BASE_DIR, "contracts", "generated")
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(save_dir, file_name)
        filled_docx.save(file_path)
        
        # 确保文件权限正确
        try:
            os.chmod(file_path, 0o644)  # 确保文件可读
        except Exception as e:
            print(f"警告: 设置文件权限失败: {str(e)}")
        
        # 构建正确的URL
        # 根据nginx配置，/files/ 映射到 /home/admin/LawReasoner-BackEnd/LawReasoner-BackEnd/contracts/
        file_url = f"{BASE_FILE_URL}/generated/{file_name}"
        
        # 启动后台任务，5分钟后删除生成的文件
        async def delete_file_after_delay(file_path, delay_minutes=5):
            await asyncio.sleep(delay_minutes * 60)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"已删除临时合同文件: {os.path.basename(file_path)}")
                else:
                    print(f"文件不存在，无需删除: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
        
        # 使用asyncio.create_task创建后台任务
        asyncio.create_task(delete_file_after_delay(file_path))
        
        print(f"生成合同成功，文件路径: {file_path}")
        print(f"生成合同成功，下载URL: {file_url}")
        
        return StandardResponse(
            code=200,
            message="生成合同成功",
            data=file_url
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"生成合同失败: {str(e)}",
            data=None
        )

@api_router.post("/contract/getRecommandContracts", response_model=StandardResponse)
async def get_recommand_contracts(request: RecommendRequest):
    try:
        global GLOBAL_MODEL

        # 配置路径和模型
        folder_path = os.path.join(BASE_DIR,"contracts",request.type,"关键词")
        model_path = os.path.join(BASE_DIR,"embed_model","all-MiniLM-L6-v2")
        index_file = os.path.join(BASE_DIR, "contracts","RAG", request.type, "knowledge_base.index")
        filenames_file = os.path.join(BASE_DIR, "contracts","RAG", request.type, "filenames.txt")
        
        # 加载模型
        if GLOBAL_MODEL is None:
            print("加载 SentenceTransformer 模型...")
            GLOBAL_MODEL = SentenceTransformer(model_path)
            
        model = GLOBAL_MODEL

        if not os.path.isfile(index_file):
            # 加载文档并生成向量
            print("加载 .txt 文件并生成向量...")
            documents = load_txt_files(folder_path)
            filenames, embeddings = generate_embeddings(documents, model)
            print(f"共加载 {len(filenames)} 个文档，每个向量维度为 {embeddings.shape[1]}")

            # 构建 FAISS 索引
            print("构建 FAISS 索引...")
            index = build_faiss_index(embeddings, embeddings.shape[1])

            # 保存索引
            print("保存 FAISS 索引...")
            faiss.write_index(index, index_file)

            # 保存文件名列表
            print("保存文件名列表...")
            with open(filenames_file, "w", encoding="utf-8") as f:
                for filename in filenames:
                    f.write(filename + "\n")
        else:
            # 直接加载索引文件
            print("加载 FAISS 索引...")
            index = load_faiss_index(index_file)

            # 加载文件名列表
            if not os.path.isfile(filenames_file):
                raise FileNotFoundError(f"文件名列表文件 '{filenames_file}' 不存在！")
            
            print("加载文件名列表...")
            with open(filenames_file, "r", encoding="utf-8") as f:
                filenames = [line.strip() for line in f.readlines()]

        # 查询
        user_input_keywords = extract_keywords(request.user_input)
        query = clean_text(user_input_keywords)
        results = search_in_knowledge_base(query, model, index, filenames, top_k=5)
        
        # 构造返回结果
        recommendations = []
        for filename, _ in results:
            filename = os.path.splitext(filename.strip())[0]
            id_response = await get_contract_id_by_name(filename, request.type)
            id_value = id_response.data if isinstance(id_response, StandardResponse) else id_response
            recommendations.append({
                "id": id_value,
                "name": filename
            })

        # 释放 hf_model 的内存
        model_to_delete = model
        model = None
        del model_to_delete  # 删除模型对象
        gc.collect()  # 调用垃圾回收器清理内存
        print("模型内存已释放！")

        return StandardResponse(
            code=200,
            message="获取推荐合同成功",
            data=recommendations
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"获取推荐合同失败: {str(e)}",
            data=[]
        )

@api_router.get("/contract/previewContract", response_model=StandardResponse)
async def preview_contract(name:str,type:str):
    try:
        preview_url = f"{BASE_FILE_URL}/{type}/{name}.docx"
        return StandardResponse(
            code=200,
            message="获取合同预览链接成功",
            data=preview_url
        )
    except Exception as e:
        return StandardResponse(
            code=500,
            message=f"获取合同预览链接失败: {str(e)}",
            data=None
        )

@api_router.get("/contract/downloadContract")
async def download_contract(name:str, type:str):
    try:
        download_url =  f"{BASE_FILE_URL}/{type}/{name}.docx"
        return StandardResponse(
            code=200,
            message="获取合同预览链接成功",
            data=download_url
        )

    except Exception as e:
        # 对于二进制响应，我们不能返回 StandardResponse，但可以记录错误
        print(f"下载合同失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载合同失败: {str(e)}")

    
