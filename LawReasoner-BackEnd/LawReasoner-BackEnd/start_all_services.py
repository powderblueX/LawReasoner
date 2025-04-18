"""
启动所有必要的服务

使用方法：
python start_all_services.py
"""
import subprocess
import sys
import os
import time
import threading
import signal
import atexit
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("start_services")

# 获取项目根目录
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# 服务命令
services = [
    {
        "name": "认证服务(auth)",
        "command": "python auth_service/main.py",
        "process": None
    },
    {
        "name": "用户资料服务(profile)",
        "command": "python profile_service/main.py",
        "process": None
    },
    {
        "name": "合同服务(contract)",
        "command": "python contract_service/main.py",
        "process": None
    },
    {
        "name": "推理服务(reasoning)",
        "command": "python reasoning_service/main.py",
        "process": None
    }
]

# 存储所有进程
processes = []

def start_service(service):
    """启动服务并输出日志"""
    logger.info(f"正在启动 {service['name']}...")
    
    # 在新进程中启动服务
    process = subprocess.Popen(
        service["command"], 
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        cwd=ROOT_DIR  # 设置工作目录为项目根目录
    )
    
    service["process"] = process
    processes.append(process)
    
    # 创建线程读取输出
    def log_output():
        for line in process.stdout:
            logger.info(f"[{service['name']}] {line.strip()}")
    
    log_thread = threading.Thread(target=log_output)
    log_thread.daemon = True  # 设为守护线程，主线程结束时自动结束
    log_thread.start()
    
    return process

def cleanup():
    """清理资源，关闭所有服务"""
    logger.info("\n正在关闭所有服务...")
    
    for process in processes:
        if process and process.poll() is None:  # 只关闭还在运行的进程
            if sys.platform == 'win32':
                # Windows下的处理方式
                process.terminate()
            else:
                # Linux/Mac的处理方式
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    
    # 等待所有进程结束
    for process in processes:
        if process:
            try:
                process.wait(timeout=5)  # 等待最多5秒
            except subprocess.TimeoutExpired:
                logger.error(f"一个服务未能正常关闭，强制结束")
                process.kill()
    
    logger.info("所有服务已关闭")

def test_db_connection():
    """测试数据库连接是否正常"""
    logger.info("测试数据库连接...")
    
    # 执行测试脚本
    result = subprocess.run(
        "python test_db_connection.py",
        shell=True,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        logger.info("数据库连接测试成功")
        return True
    else:
        logger.error(f"数据库连接测试失败: {result.stderr or result.stdout}")
        return False

def main():
    """主函数"""
    logger.info("=== 启动所有服务 ===")
    logger.info(f"工作目录: {ROOT_DIR}")
    
    # 注册退出处理函数
    atexit.register(cleanup)
    
    # 测试数据库连接
    if not test_db_connection():
        logger.error("数据库连接测试失败，无法启动服务")
        return
    
    # 启动所有服务
    for service in services:
        start_service(service)
        time.sleep(2)  # 等待服务启动
    
    logger.info("\n=== 所有服务已启动 ===")
    logger.info("按 Ctrl+C 关闭所有服务")
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(1)
            
            # 检查所有服务是否正常运行
            all_running = True
            for service in services:
                if service["process"].poll() is not None:  # 进程已结束
                    logger.error(f"{service['name']} 已意外终止，返回代码: {service['process'].returncode}")
                    all_running = False
            
            if not all_running:
                logger.error("一个或多个服务已停止，正在关闭所有服务...")
                break
                
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，正在关闭...")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 