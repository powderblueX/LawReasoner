from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form,Response
import  json,os
from app.services.contract import *
from app.core.config import settings
from pathlib import Path
from pydantic import BaseModel
from urllib.parse import quote

api_router = APIRouter()
class ContractRequest(BaseModel):
    user_input: str
    template_id: int
    type: str

class RecommendRequest(BaseModel):
    user_input: str
    type: str

GLOBAL_MODEL = None
# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BASE_FILE_URL = "http://localhost:5500"

@api_router.get("/contract/getAllName")
async def get_all_contract_name(type:str):
    lines =read_txt_file(os.path.join(BASE_DIR,"contracts","RAG",type,"filenames.txt"))

    data_list = create_data_with_ids(lines)
    return data_list

    
@api_router.get("/contract/getContractNameById")
async def get_contract_name_by_id(id:int,type:str):
    files = await get_all_contract_name(type)
    file = next((item for item in files if item['id'] == id), None)
    return file['name']

@api_router.get("/contract/getContractIdByName")
async def get_contract_id_by_name(name:str,type:str):
    files = await get_all_contract_name(type)
    file = next((item for item in files if item['name'] == name), None)
    return file['id']

@api_router.post("/contract/generateContract")
async def generate_contract(request: ContractRequest):
    contract_name = await get_contract_name_by_id(request.template_id, request.type)
    
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

    bytes_stream = fill_template_to_bytes(docx,ph_json)
    return Response(
        content=bytes_stream.getvalue(),  # 获取字节流内容
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # 设置 MIME 类型为 DOCX
        headers={"Content-Disposition": "attachment; filename=generated_contract.docx"}  # 设置下载文件名
    )

@api_router.post("/contract/getRecommandContracts")
async def get_recommand_contracts(request: RecommendRequest):
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
        id = await get_contract_id_by_name(filename,request.type)
        recommendations.append({
            "id": id,
            "name": filename
        })

    # 释放 hf_model 的内存
    del model  # 删除模型对象
    gc.collect()  # 调用垃圾回收器清理内存
    print("模型内存已释放！")

    return recommendations

@api_router.get("/contract/previewContract")
async def preview_contract(name:str,type:str):
    return f"{BASE_FILE_URL}/contracts/{type}/{name}.docx"

@api_router.get("/contract/downloadContract")
async def download_contract(name:str, type:str):
    docx_path = os.path.join(BASE_DIR,"contracts",f"{type}",f"{name}.docx")

    # 检查模板是否存在
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"未找到合同模板文件：{name}.docx")
    
    docx = Document(docx_path)
    content = template_to_bytes(docx)
    
    # 使用quote处理文件名中的中文字符
    encoded_filename = quote(f"{name}.docx")
    
    return Response(
        content=content.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
    )

    
