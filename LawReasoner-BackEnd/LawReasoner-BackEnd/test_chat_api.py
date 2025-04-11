"""
测试推理服务的聊天API
"""
import requests
import json
import sys

# 配置
API_BASE_URL = "http://localhost:8004/api/v1/reasoning"
AUTH_BASE_URL = "http://localhost:8001/api/v1/auth"

def login():
    """登录获取token"""
    login_data = {
        "username": "Xyy",  # 替换为您的用户名
        "password": "test123",  # 替换为您的密码
    }
    
    response = None
    try:
        response = requests.post(f"{AUTH_BASE_URL}/login", json=login_data)
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        print(f"登录失败: {str(e)}")
        if response and hasattr(response, 'text'):
            print(f"响应内容: {response.text}")
        sys.exit(1)

def get_sessions(token):
    """获取会话列表"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = None
    try:
        response = requests.get(f"{API_BASE_URL}/sessions", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取会话列表失败: {str(e)}")
        if response and hasattr(response, 'text'):
            print(f"响应内容: {response.text}")
        return None

def create_chat_message(token, content, session_id=None):
    """创建聊天消息"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    data = {
        "content": content
    }
    
    if session_id:
        data["session_id"] = session_id
    
    response = None
    try:
        response = requests.post(f"{API_BASE_URL}/chat", json=data, headers=headers)
        response.raise_for_status()
        return response
    except Exception as e:
        print(f"发送消息失败: {str(e)}")
        if response and hasattr(response, 'text'):
            print(f"响应内容: {response.text}")
        return None

def get_session_messages(token, session_id):
    """获取会话消息"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = None
    try:
        response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/messages", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取会话消息失败: {str(e)}")
        if response and hasattr(response, 'text'):
            print(f"响应内容: {response.text}")
        return None

def main():
    """主函数"""
    print("开始测试聊天API...")
    
    # 检查auth服务是否运行
    try:
        health_check = requests.get(f"{AUTH_BASE_URL.split('/api')[0]}/health")
        if health_check.status_code != 200:
            print("Auth服务未正常运行，请先启动auth服务！")
            return
    except Exception:
        print("Auth服务未启动，请先启动auth服务！")
        return
        
    # 检查推理服务是否运行
    try:
        health_check = requests.get(f"{API_BASE_URL.split('/api')[0]}/health")
        if health_check.status_code != 200:
            print("推理服务未正常运行，请先启动推理服务！")
            return
    except Exception:
        print("推理服务未启动，请先启动推理服务！")
        return
    
    # 登录获取token
    token = login()
    print(f"登录成功，获取到token: {token[:20]}...")
    
    # 获取会话列表
    sessions = get_sessions(token)
    print(f"获取会话列表: {json.dumps(sessions, indent=2, ensure_ascii=False)}")
    
    # 创建新会话的消息
    print("发送新消息创建会话...")
    response = create_chat_message(token, "这是一个测试消息，请简单回复")
    if response:
        print("消息发送成功，新会话已创建")
    
    # 再次获取会话列表
    print("再次获取会话列表...")
    sessions = get_sessions(token)
    print(f"更新后的会话列表: {json.dumps(sessions, indent=2, ensure_ascii=False)}")
    
    if sessions and sessions.get("sessions"):
        # 获取第一个会话的ID
        session_id = sessions["sessions"][0]["id"]
        
        # 获取会话消息
        print(f"获取会话 {session_id} 的消息...")
        messages = get_session_messages(token, session_id)
        print(f"会话消息: {json.dumps(messages, indent=2, ensure_ascii=False)}")
        
        # 在已有会话中发送消息
        print(f"在会话 {session_id} 中发送新消息...")
        response = create_chat_message(token, "这是在已有会话中的测试消息", session_id)
        if response:
            print("消息发送成功")
        
        # 再次获取会话消息
        print(f"再次获取会话 {session_id} 的消息...")
        messages = get_session_messages(token, session_id)
        print(f"更新后的会话消息: {json.dumps(messages, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    main() 