@echo off
chcp 65001 > nul
echo 开始安装LawReasoner前端依赖...

:: 创建项目目录(如果不存在)
if not exist LawReasoner mkdir LawReasoner
cd LawReasoner

:: 初始化npm项目
echo 初始化npm项目...
call npm init -y

:: 创建package.json文件
echo 配置package.json脚本...
(
echo {
echo   "name": "lawreasoner",
echo   "private": true,
echo   "version": "1.0.0", 
echo   "type": "module",
echo   "scripts": {
echo     "dev": "vite",
echo     "build": "vite build",
echo     "preview": "vite preview"
echo   }
echo }
) > package.json

:: 安装核心依赖
echo 安装Vue及相关依赖...
call npm install vue@3.5.13
call npm install vue-router@4.0.13
call npm install element-plus@2.9.5
call npm install @vue-office/docx@1.6.3
call npm install axios@1.8.1

:: 安装开发依赖
echo 安装开发依赖...
call npm install -D vite@6.2.1
call npm install -D @vitejs/plugin-vue@5.2.1
call npm install -D vite-plugin-vue-devtools@7.7.2

:: 创建基本的Vite配置文件
echo 创建Vite配置文件...
(
echo import { defineConfig } from 'vite';
echo import vue from '@vitejs/plugin-vue';
echo import VueDevTools from 'vite-plugin-vue-devtools';
echo.
echo export default defineConfig({
echo   plugins: [vue(), VueDevTools()],
echo   server: {
echo     port: 3000,
echo     open: true
echo   }
echo });
) > vite.config.js

:: 创建基本的入口文件
echo 创建入口文件...
if not exist src mkdir src
(
echo import { createApp } from 'vue';
echo import App from './App.vue';
echo import router from './router';
echo import ElementPlus from 'element-plus';
echo import 'element-plus/dist/index.css';
echo.
echo const app = createApp(App);
echo app.use(router);
echo app.use(ElementPlus);
echo app.mount('#app');
) > src\main.js

:: 创建基本App组件
echo 创建App组件...
(
echo ^<template^>
echo   ^<div^>
echo     ^<router-view/^>
echo   ^</div^>
echo ^</template^>
echo.
echo ^<script setup^>
echo // 这里可以添加组件逻辑
echo ^</script^>
echo.
echo ^<style^>
echo /* 全局样式 */
echo html, body {
echo   margin: 0;
echo   padding: 0;
echo   font-family: Arial, sans-serif;
echo }
echo ^</style^>
) > src\App.vue

:: 创建基本的index.html
echo 创建index.html...
(
echo ^<!DOCTYPE html^>
echo ^<html lang="zh-CN"^>
echo   ^<head^>
echo     ^<meta charset="UTF-8" /^>
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0" /^>
echo     ^<title^>LawReasoner^</title^>
echo   ^</head^>
echo   ^<body^>
echo     ^<div id="app"^>^</div^>
echo     ^<script type="module" src="/src/main.js"^>^</script^>
echo   ^</body^>
echo ^</html^>
) > index.html

:: 创建基本路由
echo 创建基本路由...
if not exist src\router mkdir src\router
(
echo import { createRouter, createWebHistory } from 'vue-router';
echo.
echo const routes = [
echo   {
echo     path: '/',
echo     name: 'Home',
echo     component: () => import('../views/Home.vue')
echo   }
echo ];
echo.
echo const router = createRouter({
echo   history: createWebHistory(),
echo   routes
echo });
echo.
echo export default router;
) > src\router\index.js

:: 创建示例视图
echo 创建示例视图...
if not exist src\views mkdir src\views
(
echo ^<template^>
echo   ^<div class="home"^>
echo     ^<h1^>欢迎使用 LawReasoner^</h1^>
echo     ^<p^>前端项目配置成功！^</p^>
echo   ^</div^>
echo ^</template^>
echo.
echo ^<script setup^>
echo // 这里可以添加组件逻辑
echo ^</script^>
echo.
echo ^<style scoped^>
echo .home {
echo   text-align: center;
echo   padding: 50px;
echo }
echo ^</style^>
) > src\views\Home.vue

echo 所有依赖安装完成！
echo 您现在可以运行 npm run dev 启动开发服务器
pause 