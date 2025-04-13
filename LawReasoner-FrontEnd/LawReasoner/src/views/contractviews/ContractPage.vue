<script setup>
import { ref, onMounted, defineComponent, nextTick } from 'vue';
import { ElMessage, ElButton, ElDialog, ElInput, ElScrollbar,ElTabs, ElTabPane } from 'element-plus';
import { Document, ChatSquare, Collection, Download, Loading } from '@element-plus/icons-vue';
import BackToHome from '@/components/BackToHome.vue';
import axios from 'axios';
import VueOfficeDocx from "@vue-office/docx";
import '@vue-office/docx/lib/index.css'

const BASE_URL = "http://localhost:8000"

// 消息列表
const messages = ref([]);
const inputMessage = ref('');
const isLoading = ref(false);

// 合同模板相关
const showTemplateDialog = ref(false);
const showAllTemplatesDialog = ref(false);
const selectedTemplate = ref(null);
const selectedType = ref(null); //选中的合同的类型
const recommendedTemplates = ref([]);
const allTemplatesNational = ref([]);
const allTemplatesLocal = ref([]);
const selectedContractType = ref('部委');  // 想要生成合同的类型
const generateContractFlag = ref(false);

// 调用后端 API 获取数据
const fetchTemplates = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/contract/getAllName`,{
      headers:{
        "content-type":"application/json",
        "ngrok-skip-browser-warning": "true" 
      },
      params:{
        "type":"部委"
      }
      }); 
    if (response.data && Array.isArray(response.data)) {
      allTemplatesNational.value = response.data; // 更新响应式变量
    } else {
      console.error("API返回的数据格式不正确");
    }
  } catch (error) {
    console.error("获取部委合同模板失败：", error);
  }

  try {
    const response = await axios.get(`${BASE_URL}/api/v1/contract/getAllName`,{
      headers:{
        "content-type":"application/json",
        "ngrok-skip-browser-warning": "true" 
      },
      params:{
        "type":"地方"
      }
      }); 
    if (response.data && Array.isArray(response.data)) {
      allTemplatesLocal.value = response.data; // 更新响应式变量
    } else {
      console.error("API返回的数据格式不正确");
    }
  } catch (error) {
    console.error("获取地方合同模板失败：", error);
  }
};

// 添加滚动到底部的函数
const scrollToBottom = async () => {
  await nextTick();
  const container = document.querySelector('.el-scrollbar__wrap');
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
};

// 修改 sendMessage 函数
const sendMessage = async () => {
  generateContractFlag.value = true;

  if (!inputMessage.value.trim()) return;
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  });
  
  // 滚动到底部
  await scrollToBottom();
  
  const userMessage = inputMessage.value;
  //inputMessage.value = '';
  isLoading.value = true;
  
  try {
    // 调用后端API获取推荐合同
    const response = await axios.post(`${BASE_URL}/api/v1/contract/getRecommandContracts`, {
      user_input: userMessage,
      type: selectedContractType.value
    }, {
      headers: {
        'Content-Type': 'application/json',
        "ngrok-skip-browser-warning": "69420"
      }
    });
    
    recommendedTemplates.value = response.data;
    
    // 添加系统回复和推荐模板
    messages.value.push({
      type: 'system',
      content: `根据您的需求，我为您推荐以下${selectedContractType.value}合同模板：`,
      timestamp: new Date(),
      templates: recommendedTemplates.value
    });
    
    // 滚动到底部
    await scrollToBottom();
  } catch (error) {
    console.error("获取推荐模板失败", error);
    ElMessage.error('获取推荐模板失败');
  } finally {
    isLoading.value = false;
  }
};

// 查看合同模板详情
const viewTemplate = (template, type) => {
  if (!template || !type) {
    ElMessage.warning('模板信息不完整');
    return;
  }
  selectedTemplate.value = template;
  selectedType.value = type;
  showTemplateDialog.value = true;
  
  // 加载文档预览
  loadDocxFile();
};

// 生成合同
const generateContract = async () => {
  if (!selectedTemplate.value || !selectedType.value) {
    ElMessage.warning('请先选择合同模板');
    return;
  }
  
  try {
    const response = await axios.post(`${BASE_URL}/api/v1/contract/generateContract`, {
      user_input: inputMessage.value,  // 用户输入的文本
      template_id: selectedTemplate.value.id,  // 模板ID
      type: selectedType.value  // 模板类型（部委/地方）
    }, {
      headers: {
        "ngrok-skip-browser-warning": "69420"
      },
      responseType: 'blob'  // 指定响应类型为二进制数据
    });

    // 创建 Blob URL
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
    const url = URL.createObjectURL(blob);

    // 创建下载链接
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedTemplate.value.name}.docx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // 清理 Blob URL
    URL.revokeObjectURL(url);
    
    ElMessage.success('合同生成成功');
    showTemplateDialog.value = false;
  } catch (error) {
    console.error("合同生成失败", error);
    ElMessage.error('合同生成失败');
  }
};

// 下载合同模版
const downloadTemplate = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/contract/downloadContract`, {
      headers: {
        "ngrok-skip-browser-warning": "69420"
      },
      params: {
        name: selectedTemplate.value.name,
        type: selectedType.value
      },
      responseType: 'arraybuffer'  // 修改为 arraybuffer
    });

    // 创建 Blob 对象，设置正确的 MIME 类型
    const blob = new Blob([response.data], { 
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    });

    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedTemplate.value.name}.docx`;
    document.body.appendChild(link);
    link.click();
    
    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    ElMessage.success('模板下载成功');
  } catch (error) {
    console.error("模板下载失败", error);
    ElMessage.error('模板下载失败');
  }
};

// 查看所有模板
const viewAllTemplates = () => {
  showAllTemplatesDialog.value = true;
};

// 在组件挂载时调用 API
onMounted(() => {
  fetchTemplates();
});

// 移除 defineComponent 和 export default
const docxUrl = ref(null);

// 加载后端返回的 URL
const loadDocxFile = async () => {
  try {
    const response = await axios.get(`${BASE_URL}/api/v1/contract/previewContract`,{
      headers:{
        "ngrok-skip-browser-warning": "69420",
      },
      params: {
        "name": selectedTemplate.value.name,
        "type": selectedType.value
      }
    });
    docxUrl.value = response.data;
  } catch (error) {
    console.error("获取 DOCX URL 失败", error);
  }
  console.log("name"+selectedTemplate.value.name)
  console.log("type"+selectedType.value)
  console.log("url"+docxUrl.value)
};


const onRendered = () => console.log("DOCX 文件渲染成功");
const onError = (error) => console.error("DOCX 文件渲染失败", error);
</script>

<template>
  <div class="contract-container">
    <!-- 添加标题栏 -->
    <div class="title-container">
      <img class="avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
      <span class="title">法理智推 - 智能合同生成</span>
    </div>

    <!-- 添加功能描述 -->
    <div class="feature-description">
      <div class="description-card">
        <el-icon class="description-icon"><Document /></el-icon>
        <div class="description-content">
          <h3>智能合同生成</h3>
          <p>基于您的对话描述，智能推荐合适的合同模板，并智能填写合同内容，快速生成专业法律文书</p>
        </div>
      </div>
      <div class="description-card">
        <el-icon class="description-icon"><ChatSquare /></el-icon>
        <div class="description-content">
          <h3>智能对话推荐</h3>
          <p>通过自然语言对话，理解您的合同需求，精准匹配最合适的合同模板</p>
        </div>
      </div>
      <div class="description-card">
        <el-icon class="description-icon"><Collection /></el-icon>
        <div class="description-content">
          <h3>丰富模板库</h3>
          <p>提供多种常用合同模板，涵盖商业、劳动、房产等多个领域</p>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧聊天区域 -->
      <div class="chat-section">
        <div class="messages" ref="messagesContainer">
          <el-scrollbar height="calc(100vh - 400px)">
            <div class="messages-content">
              <div 
                v-for="(message, index) in messages" 
                :key="index"
                :class="['message', message.type]"
              >
                <div v-if="message.type === 'user'" class="message-row user-message-row">
                  <div class="avatar-container">
                    <img class="chat-avatar user-avatar" src="@/assets/images/UserAvatar.png" alt="avatar">
                  </div>
                  <div class="message-content-wrapper">
                    <div class="message-content user-message">
                      {{ message.content }}
                      <div class="message-time">
                        {{ new Date(message.timestamp).toLocaleTimeString() }}
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="message-row">
                  <div class="avatar-container">
                    <img class="chat-avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
                  </div>
                  <div class="message-content-wrapper">
                    <div class="message-content system-message">
                      {{ message.content }}
                      <!-- 在系统消息中显示推荐模板 -->
                      <div v-if="message.templates" class="recommended-templates-inline">
                        <div class="template-buttons">
                          <el-button
                            v-for="template in message.templates"
                            :key="template.id"
                            type="primary"
                            plain
                            class="template-button"
                            @click="viewTemplate(template,selectedContractType)"
                          >
                            <el-icon><Document /></el-icon>
                            {{ template.name }}
                          </el-button>
                        </div>
                      </div>
                      <div class="message-time">
                        {{ new Date(message.timestamp).toLocaleTimeString() }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 加载中的消息 -->
              <div v-if="isLoading" class="message">
                <div class="message-row">
                  <div class="avatar-container">
                    <img class="chat-avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
                  </div>
                  <div class="message-content-wrapper">
                    <div class="message-content system-message">
                      <div class="loading-content">
                        <el-icon class="loading-icon"><Loading /></el-icon>
                        正在为您推荐合适的合同模板...
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-scrollbar>
        </div>
      </div>

      <!-- 右侧输入区域 -->
      <div class="input-section">
        <div class="input-header">
          <el-radio-group v-model="selectedContractType" size="large">
            <el-radio-button label="部委">部委合同</el-radio-button>
            <el-radio-button label="地方">地方合同</el-radio-button>
          </el-radio-group>
        </div>
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="5"
          placeholder="请输入您在商讨合同时的会议纪要、聊天记录等内容"
          @keyup.enter.ctrl="sendMessage"
        ></el-input>
        <div class="button-group">
          <el-button type="primary" @click="sendMessage" :loading="isLoading" class="send-button">
            <el-icon><ChatSquare /></el-icon>
            发送
          </el-button>
          <el-button @click="viewAllTemplates" class="template-button">
            <el-icon><Document /></el-icon>
            查看所有模板
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 模板详情弹窗 -->
    <el-dialog
      v-model="showTemplateDialog"
      :title="selectedTemplate?.name"
      width="70%"
      class="template-dialog"
    >
      <div class="template-content">
        <div class="template-header">
          <el-icon class="template-icon"><Document /></el-icon>
          <h3>合同模板内容</h3>
        </div>
        <div class="template-description">
          {{ selectedTemplate?.description }}
        </div>
        <div class="template-preview">
          <div class="preview-header">
            <h4>模板预览</h4>
          </div>
          <div class="preview-content">
            <vue-office-docx
                :src="docxUrl"
                style="width: 100%; height: 80vh;"
                @rendered="onRendered"
                @error="onError"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTemplateDialog = false">取消</el-button>
          <el-button type="primary" @click="downloadTemplate">
            <el-icon><Download /></el-icon> 下载模板
          </el-button>
          <el-button v-if="generateContractFlag" type="primary" @click="generateContract">
            <el-icon><Download /></el-icon> 生成合同
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 所有模板弹窗 -->
    <el-dialog
      v-model="showAllTemplatesDialog"
      title="所有合同模板"
      width="70%"
      class="all-templates-dialog"
    >
      <el-tabs>
        <el-tab-pane label="部委合同模板">
          <div class="all-templates">
            <el-scrollbar height="400px">
              <div class="template-grid">
                <div
                  v-for="template in allTemplatesNational"
                  :key="template.id"
                  class="template-card"
                  @click="viewTemplate(template, `部委`)"
                >
                  <el-icon class="template-card-icon"><Document /></el-icon>
                  <h4>{{ template.name }}</h4>
                  <p>{{ template.description }}</p>
                </div>
              </div>
            </el-scrollbar>
          </div>
        </el-tab-pane>
        <el-tab-pane label="地方合同模板">
          <div class="all-templates">
            <el-scrollbar height="400px">
              <div class="template-grid">
                <div
                  v-for="template in allTemplatesLocal"
                  :key="template.id"
                  class="template-card"
                  @click="viewTemplate(template, `地方`)"
                >
                  <el-icon class="template-card-icon"><Document /></el-icon>
                  <h4>{{ template.name }}</h4>
                  <p>{{ template.description }}</p>
                </div>
              </div>
            </el-scrollbar>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>

    <!-- 添加返回首页按钮 -->
    <BackToHome />
  </div>
</template>

<style scoped>
.contract-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  background-color: #f5f7fa;
  overflow: hidden;  /* 防止整体页面出现滚动条 */
}

.main-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 300px);
}

.chat-section {
  flex: 1;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  overflow: hidden;
}

.messages {
  flex: 1;
  padding: 20px;
  overflow: hidden;  /* 防止消息区域出现滚动条 */
}

.messages-content {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.message {
  margin-bottom: 20px;
  margin-left: 20px;
  margin-right: 20px;
  flex-shrink: 0;  /* 防止消息被压缩 */
}

.message-row {
  display: flex;
  width: 100%;
  padding: 0;
  align-items: flex-start;
  gap: 15px;
}

.user-message-row {
  flex-direction: row-reverse !important;
}

.message-content-wrapper {
  flex: 0 1 auto;
  max-width: 80%;
  min-width: 50px;
}

.user-message {
  background-color: #ecf5ff;
  color: #409eff;
  margin-right: 10px;
  margin-left: auto;
}

.system-message {
  background-color: #f0f2f5;
  margin-left: 10px;
  margin-right: auto;
}

.message-content {
  padding: 12px 16px;
  border-radius: 10px;
  position: relative;
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

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid #fff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.user-avatar {
  border: 3px solid #ecf5ff;
  box-shadow: 0 0 10px rgba(236, 245, 255, 0.5);
}

.input-section {
  width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.input-header {
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
}

.button-group {
  margin-top: 15px;
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.send-button {
  flex: 1;
  height: 40px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #409eff;
  border: none;
  transition: all 0.3s;
}

.send-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  background: #66b1ff;
}

.template-button {
  flex: 1;
  height: 40px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  transition: all 0.3s;
}

.template-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.recommended-templates-inline {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #dcdfe6;
}

.template-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-width: 100%;
  overflow-x: hidden;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.template-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.template-icon {
  font-size: 24px;
  color: #409eff;
}

.preview-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.preview-header h4 {
  margin: 0;
  color: #333;
}

.preview-content {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  min-height: 200px;
  width: 100%;
  overflow-x: auto;
}

.template-card-icon {
  font-size: 24px;
  color: #409eff;
  margin-bottom: 10px;
}

.template-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.template-card h4 {
  margin: 10px 0;
  color: #333;
}

.template-card p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.all-templates {
  padding: 10px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

:deep(.el-dialog) {
  border-radius: 8px;
  max-width: 70vw;
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__body) {
  padding: 20px;
  max-height: 85vh;
  overflow-y: auto;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.title {
  font-family: kaiTI;
  font-size: xx-large;
  font-weight: bolder;
  color: #333;
}

.feature-description {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.description-card {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.description-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.15);
}

.description-icon {
  font-size: 24px;
  color: #409eff;
  padding: 10px;
  background-color: #ecf5ff;
  border-radius: 8px;
}

.description-content h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: large;
  font-family: KaiTi;
}

.description-content p {
  margin: 0;
  color: #666;
  font-size: 16px;
  font-family: KaiTi;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

@media (max-width: 768px) {
  .feature-description {
    grid-template-columns: 1fr;
  }
  
  .description-card {
    padding: 15px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    flex-direction: column;
    height: auto;
  }

  .input-section {
    width: 100%;
  }
}
</style> 