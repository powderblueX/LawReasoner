<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage, ElButton, ElDialog, ElInput, ElScrollbar } from 'element-plus';
import { Document, ChatSquare, Collection, Download, Loading } from '@element-plus/icons-vue';
import BackToHome from '@/components/BackToHome.vue';

// 消息列表
const messages = ref([]);
const inputMessage = ref('');
const isLoading = ref(false);

// 合同模板相关
const showTemplateDialog = ref(false);
const showAllTemplatesDialog = ref(false);
const selectedTemplate = ref(null);
const recommendedTemplates = ref([]);
const allTemplates = ref([
  { id: 1, name: '房屋买卖合同', description: '适用于房屋买卖交易' },
  { id: 2, name: '劳动合同', description: '适用于用人单位与劳动者签订' },
  { id: 3, name: '租赁合同', description: '适用于房屋、设备等租赁' },
  { id: 4, name: '借款合同', description: '适用于个人或企业借款' },
  { id: 5, name: '购销合同', description: '适用于商品买卖交易' },
  { id: 6, name: '技术开发合同', description: '适用于技术开发项目' },
  { id: 7, name: '委托合同', description: '适用于委托代理事项' },
  { id: 8, name: '运输合同', description: '适用于货物运输服务' },
  { id: 9, name: '保险合同', description: '适用于各类保险业务' },
  { id: 10, name: '建设工程合同', description: '适用于工程建设项目' }
]);

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;
  
  // 添加用户消息
  messages.value.push({
    type: 'user',
    content: inputMessage.value,
    timestamp: new Date()
  });
  
  const userMessage = inputMessage.value;
  inputMessage.value = '';
  isLoading.value = true;
  
  try {
    // 模拟API调用获取推荐合同模板
    await new Promise(resolve => setTimeout(resolve, 1000));
    recommendedTemplates.value = allTemplates.value.slice(0, 5);
    
    // 添加系统回复和推荐模板
    messages.value.push({
      type: 'system',
      content: '根据您的需求，我为您推荐以下合同模板：',
      timestamp: new Date(),
      templates: recommendedTemplates.value
    });
  } catch (error) {
    ElMessage.error('获取推荐模板失败');
  } finally {
    isLoading.value = false;
  }
};

// 查看合同模板详情
const viewTemplate = (template) => {
  selectedTemplate.value = template;
  showTemplateDialog.value = true;
};

// 生成合同
const generateContract = async () => {
  try {
    // 这里应该调用后端API生成合同
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 模拟下载合同文件
    const link = document.createElement('a');
    link.href = '#';
    link.download = `${selectedTemplate.value.name}.docx`;
    link.click();
    
    ElMessage.success('合同生成成功');
    showTemplateDialog.value = false;
  } catch (error) {
    ElMessage.error('合同生成失败');
  }
};

// 查看所有模板
const viewAllTemplates = () => {
  showAllTemplatesDialog.value = true;
};
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
          <p>基于您的需求描述，智能推荐合适的合同模板，快速生成专业法律文书</p>
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

    <div class="chat-section">
      <div class="messages" ref="messagesContainer">
        <el-scrollbar height="calc(80vh - 200px)">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            :class="['message', message.type]"
          >
            <div class="message-content">
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
                    @click="viewTemplate(template)"
                  >
                    <el-icon><Document /></el-icon>
                    {{ template.name }}
                  </el-button>
                </div>
              </div>
            </div>
            <div class="message-time">
              {{ new Date(message.timestamp).toLocaleTimeString() }}
            </div>
          </div>
          
          <div v-if="isLoading" class="message system">
            <div class="message-content">
              <div class="loading-content">
                <el-icon class="loading-icon"><Loading /></el-icon>
                正在为您推荐合适的合同模板...
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
      
      <div class="input-section">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="5"
          placeholder="请输入您在商讨合同时的会议纪要、聊天记录等内容，我将帮您推荐并生成对应的合同！"
          @keyup.enter.ctrl="sendMessage"
        ></el-input>
        <div class="button-group">
          <el-button type="primary" @click="sendMessage" :loading="isLoading">
            发送
          </el-button>
          <el-button @click="viewAllTemplates">
            <el-icon><Document /></el-icon> 查看所有模板
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 模板详情弹窗 -->
    <el-dialog
      v-model="showTemplateDialog"
      :title="selectedTemplate?.name"
      width="60%"
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
            <!-- 这里可以展示合同模板的预览内容 -->
            <p>合同模板预览内容...</p>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTemplateDialog = false">取消</el-button>
          <el-button type="primary" @click="generateContract">
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
      <div class="all-templates">
        <el-scrollbar height="400px">
          <div class="template-grid">
            <div
              v-for="template in allTemplates"
              :key="template.id"
              class="template-card"
              @click="viewTemplate(template)"
            >
              <el-icon class="template-card-icon"><Document /></el-icon>
              <h4>{{ template.name }}</h4>
              <p>{{ template.description }}</p>
            </div>
          </div>
        </el-scrollbar>
      </div>
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
}

.chat-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message {
  margin-bottom: 20px;
  max-width: 80%;
}

.message.user {
  margin-left: auto;
}

.message-content {
  padding: 12px 16px;
  border-radius: 8px;
  background-color: #f0f2f5;
}

.message.user .message-content {
  background-color: #ecf5ff;
  color: #409eff;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.input-section {
  padding: 20px;
  border-top: 1px solid #ebeef5;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
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
}

.template-button {
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.template-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
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
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 20px;
  border-top: 1px solid #ebeef5;
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

@media (max-width: 768px) {
  .feature-description {
    grid-template-columns: 1fr;
  }
  
  .description-card {
    padding: 15px;
  }
}
</style> 