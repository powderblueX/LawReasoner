<script setup>
import axios from "axios";
import { getWithToken, postWithToken } from "@/axios/index.js"
import { ref, computed, nextTick, onMounted, watch } from 'vue';
import { ElButton, ElIcon, ElMessage, ElInput } from 'element-plus';
import { Promotion, Fold, Expand, DocumentCopy, Edit, Message, Histogram, Collection, Document, Check, Close } from '@element-plus/icons-vue';
import router from "@/router";
import BackToHome from '@/components/BackToHome.vue';

// 消息容器引用
const messageContainerRef = ref(null);

// 导航栏收起/展开状态
const isCollapsed = ref(false);

// 用户输入
const userInput = ref('');

// 消息列表
const messages = ref([]);

// 会话列表管理
const chatSessions = ref([]);
const currentSessionId = ref(null);

// 按时间排序的会话列表
const sortedChatSessions = computed(() => {
  return [...chatSessions.value].sort((a, b) => {
    return new Date(b.createdAt) - new Date(a.createdAt);
  });
});

// 打字机效果相关
const isTyping = ref(false);
const displayedContent = ref('');
const typingSpeed = ref(30); // 打字速度（毫秒）

// 当前会话的消息
const currentSession = computed(() => {
  return chatSessions.value.find(session => session.id === currentSessionId.value) || {
    id: null,
    title: '新会话',
    messages: []
  };
});

// 会话是否为空
const isSessionEmpty = computed(() => {
  return !currentSession.value.messages || currentSession.value.messages.length === 0;
});

// 发送状态
const isSending = ref(false);

// 会话标题编辑
const editingSessionId = ref(null);
const editingTitle = ref('');

// 打字机效果函数
const typewriterEffect = async (text) => {
  isTyping.value = true;
  displayedContent.value = '';
  
  // 检查是否为HTML内容
  const hasHtml = text.includes('<') && text.includes('>');
  
  if (hasHtml) {
    // 对于HTML内容，直接设置全部内容，不做打字机效果
    // 避免HTML标签被截断导致渲染错误
    displayedContent.value = text;
    await new Promise(resolve => setTimeout(resolve, 500)); // 短暂延迟
    isTyping.value = false;
    return;
  }
  
  // 纯文本的打字机效果
  for (let i = 0; i < text.length; i++) {
    displayedContent.value += text[i];
    // 等待一小段时间，模拟打字效果
    await new Promise(resolve => setTimeout(resolve, typingSpeed.value));
  }
  
  isTyping.value = false;
};

// 初始化：加载会话列表
onMounted(() => {
  loadChatSessions();
});

// 加载会话列表
const loadChatSessions = () => {
  console.log('开始加载会话列表');
  
  getWithToken('/api/v1/reasoning/sessions', (data) => {
    console.log('收到会话列表数据(原始):', data);
    
    // 安全地获取sessions数组
    let sessions = [];
    if (data) {
      console.log('数据类型:', typeof data);
      console.log('数据中的字段:', Object.keys(data));
      
      if (Array.isArray(data)) {
        // 如果直接返回数组
        console.log('数据是数组格式');
        sessions = data;
      } else if (data.sessions && Array.isArray(data.sessions)) {
        // 如果返回包含sessions字段的对象
        console.log('数据包含sessions字段');
        sessions = data.sessions;
      } else if (typeof data === 'object') {
        // 尝试找出可能的会话数据
        console.log('尝试解析复杂对象');
        for (const key in data) {
          if (Array.isArray(data[key])) {
            console.log(`发现数组字段: ${key}, 长度: ${data[key].length}`);
            if (data[key].length > 0 && data[key][0].id && data[key][0].title) {
              console.log(`使用${key}作为会话列表`);
              sessions = data[key];
              break;
            }
          }
        }
      } else {
        console.warn('无法识别的会话列表格式:', data);
      }
    }
    
    console.log(`解析得到${sessions.length}个会话:`, sessions);
    chatSessions.value = sessions;
    
    // 如果有会话，选择第一个或保持当前选择，否则当前会话ID设为null
    if (chatSessions.value.length > 0) {
      // 检查当前选择的会话是否还存在
      const currentSessionExists = chatSessions.value.some(s => s.id === currentSessionId.value);
      
      if (!currentSessionExists) {
        // 如果当前选择的会话不存在，切换到第一个
        console.log('当前会话不存在于列表中，切换到第一个会话');
        currentSessionId.value = chatSessions.value[0].id;
      }
      
      // 重新加载当前会话的消息
      if (currentSessionId.value) {
        console.log('加载当前会话消息:', currentSessionId.value);
        loadSessionMessages(currentSessionId.value);
      }
    } else {
      console.log('没有会话，重置当前会话ID');
      currentSessionId.value = null;
    }
  });
};

// 加载指定会话的消息历史
const loadSessionMessages = (sessionId) => {
  if (!sessionId) {
    console.warn('尝试加载消息但会话ID为空');
    return;
  }
  
  console.log(`开始加载会话ID ${sessionId} 的消息`);
  
  // 禁用之前可能存在的DOM监视器
  if (window.messageObserver) {
    window.messageObserver.disconnect();
    window.messageObserver = null;
  }
  
  getWithToken(`/api/v1/reasoning/sessions/${sessionId}/messages`, (data) => {
    console.log(`收到会话 ${sessionId} 的消息数据:`, data);
    
    // 找到当前会话
    const session = chatSessions.value.find(s => s.id === sessionId);
    if (session) {
      // 清空现有消息
      session.messages = [];
      
      // 检查数据结构
      let messagesList = [];
      if (data && data.messages && Array.isArray(data.messages)) {
        console.log(`消息列表包含 ${data.messages.length} 条消息`);
        messagesList = data.messages;
      } else if (Array.isArray(data)) {
        console.log(`消息直接作为数组返回，包含 ${data.length} 条消息`);
        messagesList = data;
      } else {
        console.warn('无法识别的消息数据格式:', data);
        return;
      }
      
      // 处理消息和响应，构建聊天记录
      messagesList.forEach(msg => {
        console.log(`处理消息ID ${msg.id}:`, msg);
        
        // 添加用户消息
        session.messages.push({
          role: 'user',
          content: msg.content,
          time: new Date(msg.created_at)
        });
        
        // 如果有响应，添加助理回复
        if (msg.response) {
          session.messages.push({
            role: 'assistant',
            content: msg.response,
            time: new Date(msg.created_at)
          });
        }
      });
      
      // 更新前端状态
      chatSessions.value = [...chatSessions.value];
      
      console.log(`会话 ${sessionId} 加载了 ${session.messages.length} 条消息`);
      
      // 使用多种方法尝试滚动到底部
      ensureScrollToBottom();
    } else {
      console.warn(`找不到ID为 ${sessionId} 的会话`);
    }
  });
};

// 新的滚动机制，使用多种方法确保滚动到底部
const ensureScrollToBottom = () => {
  console.log('开始执行滚动到底部...');
  
  // 方法1: 直接滚动
  scrollToBottom();
  
  // 方法2: 使用nextTick
  nextTick(() => {
    console.log('nextTick中执行滚动');
    scrollToBottom();
    
    // 方法3: 延迟滚动
    setTimeout(() => {
      console.log('延迟100ms后执行滚动');
      scrollToBottom();
    }, 100);
    
    // 方法4: 更长延迟滚动
    setTimeout(() => {
      console.log('延迟500ms后执行滚动');
      scrollToBottom();
    }, 500);
  });
  
  // 方法5: 使用MutationObserver监视DOM变化，当消息容器有变化时滚动
  if (messageContainerRef.value) {
    // 移除之前的观察器
    if (window.messageObserver) {
      window.messageObserver.disconnect();
    }
    
    // 创建新的观察器
    window.messageObserver = new MutationObserver((mutations) => {
      console.log('检测到DOM变化，执行滚动');
      scrollToBottom();
    });
    
    // 配置观察器
    window.messageObserver.observe(messageContainerRef.value, {
      childList: true,
      subtree: true,
      characterData: true
    });
    
    // 设置5秒后自动断开观察器，避免长时间监听
    setTimeout(() => {
      if (window.messageObserver) {
        console.log('自动断开DOM观察器');
        window.messageObserver.disconnect();
        window.messageObserver = null;
      }
    }, 5000);
  }
};

// 更强大的滚动到底部函数
const scrollToBottom = () => {
  // 方法1: 使用ref直接访问DOM
  if (messageContainerRef.value) {
    const container = messageContainerRef.value;
    console.log('使用ref滚动容器，高度:', container.scrollHeight);
    container.scrollTop = container.scrollHeight + 10000; // 加一个很大的值确保滚到底
  }
  
  // 方法2: 使用querySelector作为备份
  const messageContainer = document.querySelector('.message-container');
  if (messageContainer) {
    console.log('使用querySelector滚动容器，高度:', messageContainer.scrollHeight);
    messageContainer.scrollTop = messageContainer.scrollHeight + 10000;
  }
  
  // 方法3: 尝试滚动最后一条消息到视图
  const messages = document.querySelectorAll('.message');
  if (messages && messages.length > 0) {
    const lastMessage = messages[messages.length - 1];
    console.log('尝试将最后一条消息滚动到视图中');
    lastMessage.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }
};

// 发送消息
const sendMessage = () => {
  if (isSending.value || !userInput.value.trim()) return;
  
  const inputText = userInput.value.trim();
  isSending.value = true;
  
  console.log('准备发送消息:', inputText);
  
  // 如果没有选择会话或当前会话为空，视为新会话
  const sessionData = {
    content: inputText,
    session_id: isSessionEmpty.value ? null : currentSessionId.value
  };
  
  console.log('会话数据:', sessionData);
  
  // 添加用户消息到当前视图（临时显示）
  if (!currentSession.value.messages) {
    currentSession.value.messages = [];
  }
  
  currentSession.value.messages.push({
    role: 'user',
    content: inputText,
    time: new Date()
  });
  
  // 添加加载中的助理消息
  const assistantMessage = { 
    role: 'assistant', 
    content: '',
    isLoading: true,
    time: new Date()
  };
  currentSession.value.messages.push(assistantMessage);
  
  // 清空输入框
  userInput.value = '';
  
  // 使用新的滚动机制
  ensureScrollToBottom();
  
  // 使用 postWithToken 发送请求
  postWithToken('/api/v1/reasoning/chat', sessionData, (response) => {
    console.log('接收到chat接口响应数据:', response);
    
    // 停止加载状态，无论成功与否
    assistantMessage.isLoading = false;
    isSending.value = false;
    
    // 手动解包响应数据
    let content = '';
    let sessionId = null;
    
    // 尝试所有可能的数据结构
    if (response) {
      console.log('原始响应对象类型:', typeof response, response);
      
      if (typeof response === 'string') {
        // 直接字符串响应
        content = response;
      } 
      else if (response.response) {
        // 标准响应格式 {response: "...", session_id: 123}
        content = response.response;
        
        // 尝试不同的会话ID字段名
        if (response.session_id !== undefined) {
          sessionId = response.session_id;
        } else if (response.sessionId !== undefined) {
          sessionId = response.sessionId;
        }
      }
      else if (response.content) {
        // 其他可能格式
        content = response.content;
      }
      else if (response.answer) {
        // 其他可能格式
        content = response.answer;
      }
      else if (response.text) {
        // 其他可能格式
        content = response.text;
      }
      
      // 如果在其他地方找到会话ID
      if (!sessionId) {
        if (response.session_id !== undefined) {
          sessionId = response.session_id;
        } else if (response.sessionId !== undefined) {
          sessionId = response.sessionId;
        } else if (response.id !== undefined) {
          sessionId = response.id;
        }
      }
    }
    
    console.log('解析出内容长度:', content ? content.length : 0);
    console.log('解析出会话ID:', sessionId);
    
    // 检查是否返回了会话ID
    if (sessionId !== null && sessionId !== undefined) {
      console.log('服务器返回的会话ID类型:', typeof sessionId);
      console.log('服务器返回的会话ID值:', sessionId);
      
      // 尝试转换为数字
      let numSessionId = sessionId;
      if (typeof sessionId === 'string') {
        numSessionId = parseInt(sessionId, 10);
        console.log('转换后的会话ID:', numSessionId);
      }
      
      // 只有在需要时才更新会话ID和加载会话列表
      if (!currentSessionId.value || isSessionEmpty.value) {
        console.log('当前会话ID:', currentSessionId.value);
        console.log('会话是否为空:', isSessionEmpty.value);
        console.log('更新当前会话ID为:', numSessionId);
        
        // 设置为解析后的数字ID
        currentSessionId.value = numSessionId;
        
        // 先尝试更新当前会话的标题
        if (chatSessions.value.length > 0) {
          const existingSessionIndex = chatSessions.value.findIndex(s => s.id === numSessionId);
          if (existingSessionIndex >= 0) {
            console.log('找到已存在的会话:', existingSessionIndex);
            // 可以在这里更新会话信息
          } else {
            console.log('未找到匹配会话，需要刷新会话列表');
          }
        }
        
        // 避免频繁刷新会话列表，可能导致视图闪烁
        // 延迟加载会话列表，等待当前操作完成
        console.log('延迟加载会话列表');
        setTimeout(() => {
          console.log('开始加载会话列表');
          loadChatSessions();
        }, 500);
      } else {
        console.log('当前已有会话ID，无需更新:', currentSessionId.value);
      }
    } else {
      console.warn('服务器未返回有效的会话ID');
    }
    
    // 设置响应内容
    if (content) {
      console.log('设置助手回复, 长度:', content.length);
      
      // 检查是否包含HTML标签
      const hasHtml = content.includes('<') && content.includes('>');
      console.log('回复内容是否包含HTML:', hasHtml);
      
      // 存储完整回复
      assistantMessage.content = content;
      
      // 对于HTML内容，可以直接显示，无需打字机效果
      if (content.length > 0) {
        if (hasHtml) {
          // HTML内容可以跳过打字机效果
          console.log('HTML内容，跳过打字机效果');
          isTyping.value = false;
        } else {
          // 纯文本使用打字机效果
          console.log('纯文本内容，使用打字机效果');
          typewriterEffect(content);
        }
      }
    } else {
      console.warn('未收到有效回复');
      // 如果没有响应内容，可能是服务器错误
      assistantMessage.content = '助手没有返回有效回复';
      ElMessage.error('获取回复失败，请稍后重试');
    }
  });
};

// 复制消息内容
const copyMessage = (text) => {
  navigator.clipboard.writeText(text)
    .then(() => {
      ElMessage.success('已复制到剪贴板');
    })
    .catch(() => {
      ElMessage.error('复制失败，请手动复制');
    });
};

// 切换导航栏状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value;
};

const goToKnowledge = () => {
  router.push('/chat/knowledge');
};

// 创建新聊天
const createNewChat = () => {
  // 如果当前会话已经是空的，不需要创建新会话
  if (isSessionEmpty.value) {
    ElMessage.info('当前已经是新会话');
    return;
  }
  
  // 创建新会话
  const newSessionId = chatSessions.value.length > 0 
    ? Math.max(...chatSessions.value.map(s => s.id)) + 1 
    : 1;
  
  chatSessions.value.push({
    id: newSessionId,
    title: '新会话',
    messages: [],
    createdAt: new Date() // 添加创建时间
  });
  
  // 切换到新会话
  currentSessionId.value = newSessionId;
  
  ElMessage.success('已创建新会话');
};

// 切换到指定会话
const switchSession = (sessionId) => {
  if (currentSessionId.value === sessionId) return;
  
  currentSessionId.value = sessionId;
  
  // 重置打字机效果
  displayedContent.value = '';
  isTyping.value = false;
  
  // 加载消息
  loadSessionMessages(sessionId);
};

// 删除会话
const deleteSession = (sessionId, event) => {
  // 阻止事件冒泡，避免触发switchSession
  event.stopPropagation();
  
  // 如果只有一个会话，清空它而不是删除
  if (chatSessions.value.length === 1) {
    // 调用API删除当前会话的所有消息
    getWithToken(`/api/v1/reasoning/sessions/${sessionId}/clear`, () => {
      // 在前端更新状态
      chatSessions.value[0].messages = [];
      chatSessions.value[0].title = '新会话';
      ElMessage.success('会话已清空');
    });
    return;
  }
  
  // 找到要删除的会话索引
  const index = chatSessions.value.findIndex(s => s.id === sessionId);
  if (index === -1) return;
  
  // 调用API删除会话
  getWithToken(`/api/v1/reasoning/sessions/${sessionId}/delete`, () => {
    // 在前端删除会话
    chatSessions.value.splice(index, 1);
    
    // 如果删除的是当前会话，切换到第一个会话
    if (sessionId === currentSessionId.value) {
      currentSessionId.value = chatSessions.value[0].id;
      // 加载这个会话的消息
      loadSessionMessages(currentSessionId.value);
    }
    
    ElMessage.success('会话已删除');
  });
};

// 开始编辑标题
const startEditingTitle = (session, event) => {
  event.stopPropagation();
  editingSessionId.value = session.id;
  editingTitle.value = session.title;
};

// 保存编辑的标题
const saveSessionTitle = (sessionId) => {
  if (!editingTitle.value.trim()) {
    ElMessage.warning('标题不能为空');
    return;
  }
  
  const data = { title: editingTitle.value.trim() };
  
  postWithToken(`/api/v1/reasoning/sessions/${sessionId}/title`, data, () => {
    // 更新前端显示
    const session = chatSessions.value.find(s => s.id === sessionId);
    if (session) {
      session.title = editingTitle.value.trim();
    }
    
    // 重置编辑状态
    editingSessionId.value = null;
    editingTitle.value = '';
    
    ElMessage.success('标题已更新');
  });
};

// 取消编辑标题
const cancelEditingTitle = () => {
  editingSessionId.value = null;
  editingTitle.value = '';
};
</script>


<template>
  <div class="chat" style="min-height: 100vh;">
    <el-container>
      <!-- 左侧导航栏 -->
      <div class="nav-container" :style="{ width: isCollapsed ? '64px' : '270px' }">
        <el-aside class="nav-content" style="">
          <el-menu 
            default-active="1" class="menu-content"
            style=""
            :collapse="isCollapsed"
            >
            <div class="collapse-button" @click="toggleCollapse">
              <el-icon size="30px">
                <Expand v-if="isCollapsed" />
                <Fold v-if="!isCollapsed" />
              </el-icon>
            </div>
            <div v-if="!isCollapsed" class="nav-content-wrapper">
              <div class="title-container">
                <img class="avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
                <span class="title">法理智推</span>  
              </div>
              
              <!-- 创建新聊天按钮 -->
              <div class="new-chat">
                <el-button type="info" @click="createNewChat" class="new-chat button">
                  <el-icon><Edit /></el-icon>
                  创建新聊天
                </el-button>
              </div>
              
              <div class="chat-list">
                <div 
                  v-for="session in sortedChatSessions" 
                  :key="session.id"
                  class="chat-item"
                  :class="{ 'active-chat': session.id === currentSessionId }"
                  @click="switchSession(session.id)"
                >
                  <el-icon><Message /></el-icon>
                  <!-- 正常显示标题 -->
                  <template v-if="editingSessionId !== session.id">
                    <span class="chat-title">{{ session.title }}</span>
                    <div class="chat-item-actions">
                      <el-icon 
                        class="edit-icon" 
                        @click="startEditingTitle(session, $event)"
                      >
                        <Edit />
                      </el-icon>
                      <el-icon 
                        class="delete-icon" 
                        @click="deleteSession(session.id, $event)"
                      >
                        <el-icon class="delete-icon">×</el-icon>
                      </el-icon>
                    </div>
                  </template>
                  
                  <!-- 编辑标题 -->
                  <template v-else>
                    <el-input
                      v-model="editingTitle"
                      size="small"
                      placeholder="输入新标题"
                      @click.stop
                      class="title-input"
                    />
                    <div class="edit-actions">
                      <el-icon 
                        class="confirm-icon" 
                        @click.stop="saveSessionTitle(session.id)"
                      >
                        <Check />
                      </el-icon>
                      <el-icon 
                        class="cancel-icon" 
                        @click.stop="cancelEditingTitle"
                      >
                        <Close />
                      </el-icon>
                    </div>
                  </template>
                </div>
              </div>

              <div class="bottom-menu">
                <el-menu-item index="2" @click="goToKnowledge" class="menu-item">
                  <el-icon><Document /></el-icon>
                  <span>法律知识库</span>
                </el-menu-item>
              </div>
            </div>
          </el-menu>
        </el-aside>
      </div>

      <el-container class="main-container" :style="{ marginLeft: isCollapsed ? '64px' : '270px' }">
        <!-- <div class="profile-container">
          <div>
            <span style="font-weight: bolder; font-size: xx-large;">我是 法理智推（LawReasoner），很高兴见到您！</span>
            <p style="font-weight: bolder; font-size: large;">您可以输入民事案情，我可以通过《民法典》来帮你分析案情，并给出合理的判决结果。</p>
          </div>
        </div> -->

        <div class="chat-container">
          <!-- 消息展示区域 -->
          <div class="message-container">
            <div v-if="isSessionEmpty" class="empty-chat">
              <img class="welcome-avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
              <h2>我是 法理智推（LawReasoner），很高兴见到您！</h2>
              <p>您可以输入民事案情，我可以通过《民法典》来帮你分析案情，并给出合理的判决结果。</p>
            </div>
            <div 
              v-for="(message, index) in currentSession.messages" 
              :key="index" 
              :class="['message', message.role]"
            >
              <template v-if="message.role === 'assistant'">
                <div class="message-row">
                  <div class="avatar-container">
                    <img class="chat-avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
                  </div>
                  <div class="message-content-wrapper">
                    <div class="message-content assistant-message">
                      <!-- 加载动画 -->
                      <div v-if="message.isLoading" class="loading-animation">
                        <div class="dot-flashing"></div>
                      </div>
                      <!-- 消息内容 -->
                      <p v-else-if="message.role === 'assistant' && message === currentSession.messages[currentSession.messages.length - 1]">
                        <span v-if="isTyping" v-html="displayedContent"></span>
                        <span v-else v-html="message.content"></span>
                        <span v-if="isTyping" class="typing-cursor">|</span>
                      </p>
                      <p v-else v-html="message.content"></p>
                      <!-- 复制按钮在消息内部左下角 -->
                      <el-button
                        class="copy-button"
                        type="text"
                        @click="copyMessage(message.content)"
                      >
                        <el-icon><DocumentCopy /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="message-row user-message-row">
                  <div class="avatar-container">
                    <img class="chat-avatar user-avatar" src="@/assets/images/UserAvatar.png" alt="avatar">
                  </div>
                  <div class="message-content-wrapper">
                    <div class="message-content user-message">
                      <p>{{ message.content }}</p>
                      <!-- 复制按钮在消息内部左下角 -->
                      <el-button
                        class="copy-button"
                        type="link"
                        @click="copyMessage(message.content)"
                      >
                        <el-icon><DocumentCopy /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
              </template>
            </div>
          </div>

          <!-- 输入框区域 -->
          <div class="input-container">
            <textarea
              v-model="userInput"
              class="chat-input"
              placeholder="给 法理智推 发送消息"
              rows="2"
            ></textarea>

            <!-- 操作按钮区域 -->
            <div class="action-buttons">
              <!-- 发送按钮 -->
              <el-button
                type="primary"
                class="send-button"
                :disabled="isSending || isTyping"
                @click="sendMessage"
              >
                <template v-if="isSending || isTyping">
                  <el-icon class="is-loading"><Promotion /></el-icon>
                  <span>{{ isTyping ? '正在回复...' : '发送中...' }}</span>
                </template>
                <template v-else>
                  <el-icon><Promotion /></el-icon>
                  <span>发送</span>
                </template>
              </el-button>
            </div>
          </div>
        </div>
      </el-container>
    </el-container>
    <!-- 添加返回首页按钮 -->
    <BackToHome />
  </div>
</template>



<style scoped>
.chat {
  border-radius: 10px;
  background-color:#ffffff;
  margin: 1px;
}

.nav-container{
  position: fixed; /* 固定定位 */
  top: 0; /* 距离顶部 0 */
  left: 0; /* 距离左边 0 */
  min-height: 100vb; 
  padding-right: 10px;
}

.nav-container, 
.el-aside, 
.el-menu {
  height: 100%;
}

.nav-content{
  display: flex;
  flex-direction: column;
  height: 100vh;
  border-radius: 10px;
}

.menu-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  > div:not(.collapse-button) { 
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
  }

  background-color:#2c3e50; 
  padding-right: 10px; 
  border: 2px solid #ddd;
}

.collapse-button {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ddd;
}

.title-container{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #aceaf5;
  margin-left: 10px;
  margin-right: 10px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: 5px solid #fff; 
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5); 
  animation: blink 1s infinite alternate; 
}

.welcome-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-bottom: 20px;
  border: 5px solid #fff;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  animation: blink 1s infinite alternate;
}

.chat-avatar{
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 5px solid #fff; 
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  animation: blink 1s infinite alternate;
}

.user-avatar {
  border: 5px solid #e0f7fa;
  box-shadow: 0 0 10px rgba(224, 247, 250, 0.5);
}

@keyframes blink {
  from {
      box-shadow: 0 0 10px rgba(118, 28, 28, 0.5);
  }
  to {
      box-shadow: 0 0 20px rgba(255, 255, 255, 1);
  }
}

.title{
  font-family: KaiTi;
  color: white;
  font-weight: bolder;
  font-size: xx-large;
}

.new-chat {
  display: flex;
  justify-content: center;
  padding: 10px;
  margin: 10px;
  height: 50px;
}

.new-chat button {
  font-family: KaiTi;
  color: white;
  font-weight: bolder;
  font-size: x-large;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  &::-webkit-scrollbar {
    width: 6px;
  }
  &::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.3);
    border-radius: 3px;
  }

  padding: 10px;
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  top: 150px; /* 标题和新建聊天按钮的高度 */
  bottom: 60px; /* 法律知识库按钮的高度 */
  left: 0;
  right: 0;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
  color: #ddd;
  font-family: KaiTi;
  font-weight: bold;
}

.chat-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.active-chat {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.chat-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-icon {
  opacity: 0;
  transition: opacity 0.2s;
  font-size: 16px;
  color: #f56c6c;
}

.chat-item:hover .delete-icon {
  opacity: 1;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #666;
  text-align: center;
  padding: 0 20px;
  font-family: KaiTi;
  font-size: large;
}

.menu-item {
  font-family: KaiTi;
  color: white;
  font-weight: bolder;
  font-size: large;
  margin-top: 5px;
  width: 100%;
}

.main-container{
  display: flex;
  flex-direction: column;
}

/* .profile-container{
  margin-top: 15px;
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 100vh;
  align-items: center;
  font-family: KaiTi;
  border-bottom: 3px solid #89c1d4;
} */

.chat-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 100vh;
  border-radius: 8px;
  align-items: center;
}

.input-container {
  display: flex;
  width: 100%;
  max-width: 800px;
  height: 100px;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  position: fixed;
  bottom: 0;
  background-color: #fff;
  border-bottom: 1px solid #ccc;
  border-radius: 20px;
  padding: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.chat-input {
  flex: 1;
  padding: 10px;
  height: 80%;
  border: 1px solid #ddd;
  border-radius: 15px;
  font-size: 20px;
  resize: none;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.send-button{
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.send-button:hover {
  background-color: #f0f4f8;
  transform: translateY(-2px);
}

.message-container {
  flex: 1;
  width: 80%; 
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 20px;
  overflow-y: auto;
  padding-bottom: 150px;
}

.message {
  display: flex;
  width: 100%;
  margin-bottom: 15px;
}

.message-row {
  display: flex;
  width: 100%;
  padding: 0 10px;
  align-items: flex-start;
  gap: 15px;
}

.user-message-row {
  flex-direction: row-reverse;
  justify-content: flex-start;
}

.message-content-wrapper {
  flex: 0 1 auto;
  max-width: 85%;
  min-width: 50px;
}

.user-message {
  background-color: #e0f7fa;
  margin-right: 10px;
  margin-left: auto;
}

.assistant-message {
  background-color: #f0f0f0;
  margin-left: 10px;
  margin-right: auto;
}

.message-content {
  padding: 10px 15px;
  border-radius: 10px;
  position: relative;
  padding-bottom: 30px;
  word-break: break-word;
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.avatar-container {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 加载动画样式 */
.dot-flashing {
  position: relative;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #409eff;
  color: #409eff;
  animation: dotFlashing 1s infinite linear alternate;
  animation-delay: .5s;
}

.dot-flashing::before, .dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
}

.dot-flashing::before {
  left: -15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #409eff;
  color: #409eff;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 15px;
  width: 10px;
  height: 10px;
  border-radius: 5px;
  background-color: #409eff;
  color: #409eff;
  animation: dotFlashing 1s infinite alternate;
  animation-delay: 1s;
}

@keyframes dotFlashing {
  0% {
    background-color: #409eff;
  }
  50%,
  100% {
    background-color: rgba(64, 158, 255, 0.2);
  }
}

.loading-animation {
  padding: 10px;
}

/* 禁用状态样式 */
.send-button.is-disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.typing-cursor {
  display: inline-block;
  width: 2px;
  height: 1em;
  background-color: #409EFF;
  margin-left: 2px;
  animation: cursor-blink 1s infinite;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.nav-content-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
}

.bottom-menu {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background-color: #2c3e50;
  z-index: 1;
}

.copy-button-container {
  display: flex;
  justify-content: center;
  margin-top: 5px;
}

.copy-button {
  opacity: 0.5;
  transition: opacity 0.2s;
  font-size: 14px;
  padding: 2px 8px;
  position: absolute;
  left: 5px;
  bottom: 2px;
}

.copy-button:hover {
  opacity: 1;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}

.user-header {
  justify-content: flex-end;
}

.chat-item-actions {
  display: flex;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.2s;
}

.chat-item:hover .chat-item-actions {
  opacity: 1;
}

.edit-icon {
  color: #409EFF;
  font-size: 16px;
}

.title-input {
  flex: 1;
  margin-right: 5px;
}

.edit-actions {
  display: flex;
  gap: 5px;
}

.confirm-icon {
  color: #67C23A;
  font-size: 16px;
}

.cancel-icon {
  color: #F56C6C;
  font-size: 16px;
}

/* 让HTML内容正确显示 */
.message-content :deep(p) {
  margin-bottom: 8px;
}

.message-content :deep(ol),
.message-content :deep(ul) {
  padding-left: 20px;
  margin-bottom: 10px;
}

.message-content :deep(li) {
  margin-bottom: 4px;
}

.message-content :deep(strong),
.message-content :deep(b) {
  font-weight: bold;
}

.message-content :deep(pre),
.message-content :deep(code) {
  background-color: #f0f0f0;
  border-radius: 3px;
  padding: 2px 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>