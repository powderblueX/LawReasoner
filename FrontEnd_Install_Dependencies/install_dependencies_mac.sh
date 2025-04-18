#!/bin/bash

echo "开始为macOS安装LawReasoner前端依赖..."

# 检查是否安装了Homebrew
if ! command -v brew &> /dev/null; then
    echo "未检测到Homebrew，正在安装..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew已安装，正在更新..."
    brew update
fi

# 检查并安装Node.js
if ! command -v node &> /dev/null; then
    echo "未检测到Node.js，正在安装..."
    brew install node
else
    echo "Node.js已安装: $(node -v)"
fi

# 创建项目目录(如果不存在)
mkdir -p LawReasoner
cd LawReasoner

# 初始化npm项目
echo "初始化npm项目..."
npm init -y

# 创建package.json文件
echo "配置package.json脚本..."
cat > package.json << 'EOF'
{
  "name": "lawreasoner",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
EOF

# 使用更快的淘宝镜像（可选）
echo "配置npm淘宝镜像以加速下载..."
npm config set registry https://registry.npmmirror.com

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

# 创建基本的Vite配置文件
echo "创建Vite配置文件..."
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import VueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig({
  plugins: [vue(), VueDevTools()],
  server: {
    port: 3000,
    open: true
  }
});
EOF

# 创建目录结构
mkdir -p src/router src/views

# 创建基本的入口文件
echo "创建入口文件..."
cat > src/main.js << 'EOF'
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

const app = createApp(App);
app.use(router);
app.use(ElementPlus);
app.mount('#app');
EOF

# 创建基本App组件
echo "创建App组件..."
cat > src/App.vue << 'EOF'
<template>
  <div>
    <router-view/>
  </div>
</template>

<script setup>
// 这里可以添加组件逻辑
</script>

<style>
/* 全局样式 */
html, body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
}
</style>
EOF

# 创建基本的index.html
echo "创建index.html..."
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LawReasoner</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
EOF

# 创建基本路由
echo "创建基本路由..."
cat > src/router/index.js << 'EOF'
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
EOF

# 创建示例视图
echo "创建示例视图..."
cat > src/views/Home.vue << 'EOF'
<template>
  <div class="home">
    <h1>欢迎使用 LawReasoner</h1>
    <p>前端项目配置成功！</p>
  </div>
</template>

<script setup>
// 这里可以添加组件逻辑
</script>

<style scoped>
.home {
  text-align: center;
  padding: 50px;
}
</style>
EOF

echo "所有依赖安装完成！"
echo "您可以通过以下命令启动开发服务器：npm run dev" 