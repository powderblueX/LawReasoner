# 法理智推系统后端

这是一个基于微服务架构的法理智推系统后端，使用Python FastAPI框架开发。

## 项目结构

- `api_gateway`：API网关服务，处理所有外部请求的入口
- `auth_service`：认证和授权服务，处理用户登录和权限管理
- `reasoning_service`：法律推理服务，核心法理推理引擎
- `knowledge_service`：知识库服务，管理法律知识图谱和规则库
- `common`：共享工具和模型
- `config`：配置文件

## 安装和运行

### 创建并激活虚拟环境

```bash
conda env create -f environment.yml
conda activate law-reasoner
```

### 启动服务（开发环境）

```bash
# 启动API网关
cd api_gateway
uvicorn main:app --reload --port 8000

# 启动认证服务
cd auth_service
uvicorn main:app --reload --port 8001

# 启动推理服务
cd reasoning_service
uvicorn main:app --reload --port 8002

# 启动知识库服务
cd knowledge_service
uvicorn main:app --reload --port 8003
```

## 部署
系统设计适用于在Ubuntu环境下部署，可通过Docker或直接部署到魔搭平台上。 