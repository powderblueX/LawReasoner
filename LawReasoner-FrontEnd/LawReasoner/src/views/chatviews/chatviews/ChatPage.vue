<script setup>
import axios from "axios";
import {post} from "@/axios/index.js"
import { ref } from 'vue';
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

// 发送状态
const isSending = ref(false);


// 发送消息
const sendMessage = () => {
  if (isSending.value || !userInput.value.trim()) return;
  
  const inputText = userInput.value.trim();
  isSending.value = true;
  
  // 添加用户消息
  messages.value.push({ 
    role: 'user', 
    content: inputText 
  });
  
  // 添加加载中的助理消息
  const assistantMessage = { 
    role: 'assistant', 
    content: '',
    isLoading: true
  };
  messages.value.push(assistantMessage);
  
  // 清空输入框
  userInput.value = '';

  // 发起请求
  fetch('https://concrete-informed-iguana.ngrok-free.app/deepseek', {
    method: 'POST',
    headers: {
      "ngrok-skip-browser-warning": "true",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ "message": inputText })
  })
  .then(response => response.json())
  .then(data => {
    // 更新消息状态
    assistantMessage.content = data.answer;
    assistantMessage.isLoading = false;
    messages.value = [...messages.value]; // 触发响应式更新
  })
  .catch(error => {
    assistantMessage.content = '请求失败，请稍后重试';
    assistantMessage.isLoading = false;
    messages.value = [...messages.value];
    console.error('Error:', error);
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

const goToHistory = () => {
  router.push('/chat/history');
};

const goToCommunity = () => {
  router.push('/chat/community');
};

// const goToDocument = () => {
//   router.push('/document');
// };

// 创建新聊天
const createNewChat = () => {
  // 清空消息列表
  messages.value = [];
  ElMessage.success('已创建新会话');
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
            <div v-if="!isCollapsed">
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
                
              </div>

              <el-menu-item index="2" @click="goToKnowledge" class="menu-item">
                <el-icon><Document /></el-icon>
                <span>法律知识库</span>
              </el-menu-item>

              <el-menu-item index="3" @click="goToHistory" class="menu-item">
                <el-icon><Histogram /></el-icon>
                <span>历史会话</span>
              </el-menu-item>

              <el-menu-item index="4" @click="goToCommunity" class="menu-item">
                <el-icon><Message /></el-icon>
                <span>案例社区</span>
              </el-menu-item>

              <!-- <el-menu-item index="5" @click="goToDocument" class="menu-item">
                <el-icon><Collection /></el-icon>
                <span>法律文书</span>
              </el-menu-item> -->

            </div>
          </el-menu>
        </el-aside>
      </div>

      <el-container class="main-container" :style="{ marginLeft: isCollapsed ? '64px' : '270px' }">
        <div class="profile-container">
          <!-- <img class="avatar" src="@/assets/images/LawReasoner.png" alt="avatar"> -->
          <div>
            <span style="font-weight: bolder; font-size: xx-large;">我是 法理智推（LawReasoner），很高兴见到您！</span>
            <p style="font-weight: bolder; font-size: large;">您可以输入民事案情，我可以通过《民法典》来帮你分析案情，并给出合理的判决结果。</p>
          </div>
        </div>

        <div class="chat-container">
          <!-- 消息展示区域 -->
          <div class="message-container">
            <div v-for="(message, index) in messages" :key="index" :class="['message', message.role]">
              <template v-if="message.role === 'assistant'">
                <div style="display: flex;">
                  <img class="chat-avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
                </div>
                <div class="message-content assistant-message">
                  <!-- 加载动画 -->
                  <div v-if="message.isLoading" class="loading-animation">
                    <div class="dot-flashing"></div>
                  </div>
                  <!-- 消息内容 -->
                  <p v-html="message.content"></p>
                  <!-- 复制按钮 -->
                  <el-button
                    class="copy-button"
                    type="text"
                    @click="copyMessage(message.content)"
                  >
                    <el-icon><DocumentCopy /></el-icon>
                  </el-button>
                </div>
              </template>
              <template v-else>
                <div class="message-content user-message">
                  <p>{{ message.content }}</p>
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
                :disabled="isSending"
                @click="sendMessage"
              >
                <template v-if="isSending">
                  <el-icon class="is-loading"><Promotion /></el-icon>
                  <span>发送中...</span>
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
  margin-top: auto;

  font-family: KaiTi;
  color: white;
  font-weight: bolder;
  font-size: large;
}

.menu-item {
  font-family: KaiTi;
  color: white;
  font-weight: bolder;
  font-size: large;
  margin-top: 5px;
}

.main-container{
  display: flex;
  flex-direction: column;
}

.profile-container{
  margin-top: 15px;
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  width: 100%;
  min-width: 100vh;
  align-items: center;
  font-family: KaiTi;
  border-bottom: 3px solid #89c1d4;
}

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
  align-items: flex-start;
  gap: 10px;
}

.message-content {
  padding-top: 5px;
  padding-left: 10px;
  padding-right: 10px;
  border-radius: 10px;
  max-width: 60%;
  min-width: 50px;
}

.user-message {
  align-self: flex-end;
  background-color: #e0f7fa;
}

.assistant-message {
  align-self: center;
  background-color: #f0f0f0;
}

.chat-avatar{
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 5px solid #fff; 
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5); 
}

.message.user {
  justify-content: flex-end; 
}

.message.assistant {
  justify-content: flex-start; 
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
</style>