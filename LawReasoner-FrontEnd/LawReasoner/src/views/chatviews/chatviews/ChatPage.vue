<script setup>
import axios from "axios";
import {post} from "@/axios/index.js"
import { ref, computed, nextTick } from 'vue';
import { ElButton, ElIcon, ElMessage } from 'element-plus';
import { Promotion, Fold, Expand, DocumentCopy, Edit, Message, Histogram, Collection, Document } from '@element-plus/icons-vue';
import router from "@/router";
import BackToHome from '@/components/BackToHome.vue';
// 导航栏收起/展开状态
const isCollapsed = ref(false);

// 用户输入
const userInput = ref('');

// 消息列表
const messages = ref([]);

// 会话列表管理
const chatSessions = ref([
  {
    id: 1,
    title: '新会话',
    messages: [],
    createdAt: new Date() // 添加创建时间
  }
]);
const currentSessionId = ref(1);

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
  return chatSessions.value.find(session => session.id === currentSessionId.value) || chatSessions.value[0];
});

// 会话是否为空
const isSessionEmpty = computed(() => {
  return currentSession.value.messages.length === 0;
});

// 发送状态
const isSending = ref(false);

// 打字机效果函数
const typewriterEffect = async (text) => {
  isTyping.value = true;
  displayedContent.value = '';
  
  for (let i = 0; i < text.length; i++) {
    displayedContent.value += text[i];
    // 等待一小段时间，模拟打字效果
    await new Promise(resolve => setTimeout(resolve, typingSpeed.value));
  }
  
  isTyping.value = false;
};

// 发送消息
const sendMessage = () => {
  if (isSending.value || !userInput.value.trim()) return;
  
  const inputText = userInput.value.trim();
  isSending.value = true;
  
  // 添加用户消息到当前会话
  const userMessage = { role: 'user', content: inputText };
  currentSession.value.messages.push(userMessage);
  
  // 更新会话的创建时间
  currentSession.value.createdAt = new Date();
  
  // 添加加载中的助理消息
  const assistantMessage = { 
    role: 'assistant', 
    content: '',
    isLoading: true
  };
  currentSession.value.messages.push(assistantMessage);
  
  // 更新会话标题（使用用户消息的前10个字符作为标题）
  if (currentSession.value.messages.length === 2) {
    currentSession.value.title = inputText.length > 10 
      ? inputText.substring(0, 10) + '...' 
      : inputText;
  }
  
  // 清空输入框
  userInput.value = '';

  // 发起请求到后端API
  fetch('http://127.0.0.1:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ 
      message: inputText,
      session_id: currentSessionId.value
    })
  })
  .then(async response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  })
  .then(data => {
    // 更新消息状态
    assistantMessage.content = data.answer;
    assistantMessage.isLoading = false;
    
    // 使用打字机效果显示回答
    nextTick(() => {
      typewriterEffect(data.answer);
    });
    
    // 触发响应式更新
    chatSessions.value = [...chatSessions.value];
  })
  .catch(error => {
    console.error('Error details:', error);
    assistantMessage.content = `请求失败：${error.message}`;
    assistantMessage.isLoading = false;
    chatSessions.value = [...chatSessions.value];
    ElMessage.error(`请求失败：${error.message}`);
  })
  .finally(() => {
    isSending.value = false;
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
  currentSessionId.value = sessionId;
  // 重置打字机效果
  displayedContent.value = '';
  isTyping.value = false;
};

// 删除会话
const deleteSession = (sessionId, event) => {
  // 阻止事件冒泡，避免触发switchSession
  event.stopPropagation();
  
  // 如果只有一个会话，清空它而不是删除
  if (chatSessions.value.length === 1) {
    chatSessions.value[0].messages = [];
    chatSessions.value[0].title = '新会话';
    ElMessage.success('会话已清空');
    return;
  }
  
  // 找到要删除的会话索引
  const index = chatSessions.value.findIndex(s => s.id === sessionId);
  if (index === -1) return;
  
  // 删除会话
  chatSessions.value.splice(index, 1);
  
  // 如果删除的是当前会话，切换到第一个会话
  if (sessionId === currentSessionId.value) {
    currentSessionId.value = chatSessions.value[0].id;
  }
  
  ElMessage.success('会话已删除');
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
                  <span class="chat-title">{{ session.title }}</span>
                  <el-icon 
                    class="delete-icon" 
                    @click="deleteSession(session.id, $event)"
                  >
                    <el-icon class="delete-icon">×</el-icon>
                  </el-icon>
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
                        <span v-if="isTyping">{{ displayedContent }}</span>
                        <span v-else>{{ message.content }}</span>
                        <span v-if="isTyping" class="typing-cursor">|</span>
                      </p>
                      <p v-else>{{ message.content }}</p>
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
</style>