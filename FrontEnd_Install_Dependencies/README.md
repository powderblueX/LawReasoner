# LawReasoner 环境配置说明

## 前端依赖安装

本项目提供了三个脚本用于自动安装所需的前端依赖：

### Windows 用户

1. 双击运行 `install_dependencies.bat` 文件
2. 脚本将自动创建项目目录并安装所有必要的依赖

### macOS 用户（推荐）

1. 打开终端，进入项目根目录
2. 执行以下命令赋予脚本执行权限：
   ```
   chmod +x install_dependencies_mac.sh
   ```
3. 运行脚本：
   ```
   ./install_dependencies_mac.sh
   ```
4. 该脚本会自动检查并安装Homebrew、Node.js，并使用淘宝镜像加速依赖下载

### Linux/其他Unix用户

1. 打开终端，进入项目根目录
2. 执行以下命令赋予脚本执行权限：
   ```
   chmod +x install_dependencies.sh
   ```
3. 运行脚本：
   ```
   ./install_dependencies.sh
   ```

## 已包含的依赖

脚本将安装以下依赖：

### 核心依赖
- Vue 3.5.13
- Vue Router 4.0.13
- Element Plus 2.9.5
- @vue-office/docx 1.6.3
- Axios 1.8.1

### 开发依赖
- Vite 6.2.1
- @vitejs/plugin-vue 5.2.1
- vite-plugin-vue-devtools 7.7.2

## 注意事项

- 确保您的系统已安装 Node.js 和 npm（macOS脚本会自动安装这些）
- 如果安装过程中遇到问题，请确保网络连接正常并尝试使用管理员/sudo权限运行脚本
- macOS用户可能需要输入管理员密码来安装Homebrew 