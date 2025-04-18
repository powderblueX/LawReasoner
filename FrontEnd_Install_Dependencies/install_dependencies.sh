#!/bin/bash

echo "开始安装LawReasoner前端依赖..."

# 创建项目目录(如果不存在)
mkdir -p LawReasoner
cd LawReasoner

# 初始化npm项目
echo "初始化npm项目..."
npm init -y

# 安装核心依赖
echo "安装Vue及相关依赖..."
npm install vue@3.5.13
npm install vue-router@4.0.13
npm install element-plus@2.9.5
npm install @vue-office/docx@1.6.3
npm install axios@1.8.1

# 安装开发依赖
echo "安装开发依赖..."
npm install -D vite@6.2.1
npm install -D @vitejs/plugin-vue@5.2.1
npm install -D vite-plugin-vue-devtools@7.7.2

echo "所有依赖安装完成！" 