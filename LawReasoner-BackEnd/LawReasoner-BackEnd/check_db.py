#!/usr/bin/env python
"""
数据库检查脚本
用于检查users表中的用户信息
"""
import os
import sys
import sqlite3
import json
from datetime import datetime

def format_timestamp(timestamp):
    """将时间戳格式化为可读形式"""
    try:
        return datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(timestamp)

def check_database(db_path):
    """检查数据库中的用户信息"""
    print(f"检查数据库: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        cursor = conn.cursor()
        
        # 检查users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("错误: users表不存在!")
            
            # 列出所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            if tables:
                print("数据库中存在的表:")
                for table in tables:
                    print(f"  - {table['name']}")
            else:
                print("数据库中没有任何表!")
            
            return
        
        # 获取表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n表结构:")
        for col in columns:
            print(f"  {col['name']} ({col['type']})")
        
        # 获取用户数量
        cursor.execute("SELECT COUNT(*) as count FROM users")
        count = cursor.fetchone()['count']
        print(f"\n共有 {count} 个用户记录")
        
        # 获取所有用户
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("没有找到任何用户记录!")
        else:
            print("\n用户列表:")
            for i, user in enumerate(users, 1):
                user_dict = {key: user[key] for key in user.keys()}
                
                # 格式化时间戳
                if 'created_at' in user_dict:
                    user_dict['created_at'] = format_timestamp(user_dict['created_at'])
                if 'updated_at' in user_dict:
                    user_dict['updated_at'] = format_timestamp(user_dict['updated_at'])
                
                # 不显示密码
                if 'hashed_password' in user_dict:
                    user_dict['hashed_password'] = "[已隐藏]"
                
                print(f"\n用户 {i}:")
                for key, value in user_dict.items():
                    print(f"  {key}: {value}")
        
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {str(e)}")

def main():
    """主函数"""
    # 检查共享数据库
    db_paths = [
        "./common_db/shared_db.db",  # 共享数据库
        "./auth_service/auth_service.db",  # auth_service数据库
        "./auth_service.db",  # 根目录数据库
    ]
    
    # 添加命令行参数
    if len(sys.argv) > 1:
        db_paths.insert(0, sys.argv[1])
    
    found = False
    for db_path in db_paths:
        if os.path.exists(db_path):
            found = True
            check_database(db_path)
            print("\n" + "-"*50 + "\n")
    
    if not found:
        print("未找到任何数据库文件!")
        print("请指定数据库路径作为参数，例如: python check_db.py path/to/your/database.db")

if __name__ == "__main__":
    main() 