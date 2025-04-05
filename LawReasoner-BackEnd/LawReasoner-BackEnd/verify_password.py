#!/usr/bin/env python
"""
密码验证测试脚本
用于测试特定用户名和密码是否匹配
"""
import os
import sys
import sqlite3
from passlib.context import CryptContext

# 添加项目根目录到sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 模拟auth_service中的密码验证函数
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码与哈希值是否匹配"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"验证密码时出错: {str(e)}")
        return False

def test_user_password(db_path, username, plain_password):
    """测试指定用户名和密码是否匹配"""
    print(f"测试用户 '{username}' 的密码...")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户信息
        cursor.execute("SELECT id, username, email, hashed_password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"错误: 找不到用户 '{username}'")
            
            # 查询所有用户
            cursor.execute("SELECT id, username, email FROM users")
            all_users = cursor.fetchall()
            if all_users:
                print("数据库中存在的用户:")
                for u in all_users:
                    print(f"  - ID: {u[0]}, 用户名: {u[1]}, 邮箱: {u[2]}")
            else:
                print("数据库中没有任何用户!")
            
            return False
        
        user_id, username, email, hashed_password = user
        print(f"找到用户 '{username}' (ID: {user_id})")
        print(f"存储的密码哈希: {hashed_password[:10]}...（前10字符）")
        
        # 测试密码
        is_valid = verify_password(plain_password, hashed_password)
        
        if is_valid:
            print(f"密码验证成功! 用户 '{username}' 的密码匹配。")
        else:
            print(f"密码验证失败! 用户 '{username}' 的密码不匹配。")
            
            # 检查哈希格式
            if hashed_password.startswith("$2b$"):
                print("密码使用了bcrypt哈希格式")
            elif hashed_password.startswith("$pbkdf2"):
                print("密码使用了PBKDF2哈希格式")
            elif len(hashed_password) == 64 and all(c in "0123456789abcdef" for c in hashed_password.lower()):
                print("密码可能使用了SHA-256/SHA-512哈希格式（不带盐）")
            else:
                print(f"无法识别的密码哈希格式")
        
        # 尝试创建一个相同密码的新哈希，看它的格式
        new_hash = pwd_context.hash(plain_password)
        print(f"使用同样密码生成的新哈希: {new_hash[:20]}...（前20字符）")
        
        conn.close()
        return is_valid
        
    except Exception as e:
        print(f"测试密码时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def update_user_password(db_path, username, new_password):
    """更新用户密码"""
    print(f"更新用户 '{username}' 的密码...")
    
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取用户ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"错误: 找不到用户 '{username}'")
            return False
        
        user_id = user[0]
        
        # 生成新密码哈希
        new_hash = pwd_context.hash(new_password)
        print(f"为 '{username}' 生成新的密码哈希")
        
        # 更新密码
        cursor.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (new_hash, user_id))
        conn.commit()
        
        print(f"用户 '{username}' 的密码已更新!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"更新密码时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # 数据库路径 - 使用共享数据库
    db_path = "./common_db/shared_db.db"
    
    # 测试用户名和密码
    username = "Xyy"  # 您提到的用户名
    password = "password"  # 尝试的密码
    
    # 测试密码
    test_result = test_user_password(db_path, username, password)
    
    # 如果测试失败，询问是否要重置密码
    if not test_result:
        response = input("是否要重置该用户的密码? (y/n): ")
        if response.lower() == 'y':
            new_password = "password123"  # 新密码
            update_user_password(db_path, username, new_password)
            print(f"密码已重置为: {new_password}")
            
            # 再次测试
            print("\n重新测试新密码...")
            test_user_password(db_path, username, new_password) 