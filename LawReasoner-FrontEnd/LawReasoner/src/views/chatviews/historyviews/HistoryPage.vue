<script setup>
import { ref, onMounted } from 'vue';
import { ElButton, ElInput, ElTag, ElPopconfirm, ElDatePicker, ElEmpty } from 'element-plus';
import { Search, Delete, Edit, Document, ArrowRight } from '@element-plus/icons-vue';
import router from '@/router';
import BackToHome from '@/components/BackToHome.vue';

// 历史会话数据
const chatHistory = ref([
  {
    id: 1,
    title: '关于房屋租赁合同纠纷的咨询',
    tags: ['合同纠纷', '房屋租赁'],
    date: '2023-09-15 14:30',
    preview: '我租了一套房子，但是房东要提前终止合同...'
  },
  {
    id: 2,
    title: '工伤赔偿问题咨询',
    tags: ['劳动纠纷', '工伤赔偿'],
    date: '2023-09-10 09:15',
    preview: '我在公司工作期间发生了意外，想咨询一下工伤赔偿的相关问题...'
  },
  {
    id: 3,
    title: '婚姻家庭财产分割问题',
    tags: ['婚姻家庭', '财产分割'],
    date: '2023-09-05 16:45',
    preview: '离婚后，共同财产如何分割才合理...'
  }
]);

// 搜索和筛选相关
const searchKeyword = ref('');
const dateRange = ref([]);

// 编辑标题弹窗状态
const editTitleId = ref(null);
const newTitle = ref('');

// 继续聊天
const continueChat = (id) => {
  // 跳转到聊天页面，并传递会话ID
  router.push({
    path: '/chat',
    query: { historyId: id }
  });
};

// 删除聊天记录
const deleteHistory = (id) => {
  const index = chatHistory.value.findIndex(item => item.id === id);
  if (index !== -1) {
    chatHistory.value.splice(index, 1);
  }
};

// 编辑标题
const startEditTitle = (id, title) => {
  editTitleId.value = id;
  newTitle.value = title;
};

const saveTitle = (id) => {
  const index = chatHistory.value.findIndex(item => item.id === id);
  if (index !== -1 && newTitle.value.trim()) {
    chatHistory.value[index].title = newTitle.value;
  }
  editTitleId.value = null;
};

// 搜索和筛选
const filteredHistory = () => {
  return chatHistory.value.filter(item => {
    // 关键词搜索
    const keywordMatch = !searchKeyword.value || 
      item.title.includes(searchKeyword.value) || 
      item.preview.includes(searchKeyword.value) ||
      item.tags.some(tag => tag.includes(searchKeyword.value));
    
    // 日期筛选
    let dateMatch = true;
    if (dateRange.value && dateRange.value.length === 2) {
      const itemDate = new Date(item.date);
      const startDate = new Date(dateRange.value[0]);
      const endDate = new Date(dateRange.value[1]);
      dateMatch = itemDate >= startDate && itemDate <= endDate;
    }
    
    return keywordMatch && dateMatch;
  });
};
</script>

<template>
  <div class="history-container">
    <h1 class="page-title">历史会话</h1>
    
    <div class="filter-section">
      <div class="search-box">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索会话标题、内容或标签" 
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <div class="date-filter">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
        />
      </div>
    </div>
    
    <div class="history-list">
      <el-empty v-if="filteredHistory().length === 0" description="没有找到相关会话记录" />
      
      <div 
        v-for="chat in filteredHistory()" 
        :key="chat.id"
        class="history-item"
      >
        <div class="history-content">
          <div class="history-header">
            <div v-if="editTitleId === chat.id" class="edit-title">
              <el-input 
                v-model="newTitle" 
                placeholder="输入新标题" 
                size="small"
              />
              <el-button 
                type="primary" 
                size="small" 
                @click="saveTitle(chat.id)"
                class="save-btn"
              >
                保存
              </el-button>
            </div>
            <h2 v-else class="history-title">{{ chat.title }}</h2>
            
            <div class="history-date">{{ chat.date }}</div>
          </div>
          
          <div class="history-tags">
            <el-tag 
              v-for="(tag, index) in chat.tags" 
              :key="index"
              size="small"
              effect="plain"
              class="tag"
            >
              {{ tag }}
            </el-tag>
          </div>
          
          <p class="history-preview">{{ chat.preview }}</p>
        </div>
        
        <div class="history-actions">
          <el-button 
            type="primary" 
            size="small" 
            @click="continueChat(chat.id)"
            class="continue-btn"
          >
            继续会话 <el-icon><ArrowRight /></el-icon>
          </el-button>
          
          <div class="action-buttons">
            <el-button 
              type="text" 
              @click="startEditTitle(chat.id, chat.title)"
              class="edit-btn"
            >
              <el-icon><Edit /></el-icon>
            </el-button>
            
            <el-popconfirm
              title="确定要删除这条会话记录吗？"
              @confirm="deleteHistory(chat.id)"
            >
              <template #reference>
                <el-button type="text" class="delete-btn">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 添加返回首页按钮 -->
    <BackToHome />
  </div>
</template>

<style scoped>
.history-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-title {
  font-family: 'KaiTi', serif;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  margin-right: 20px;
}

.history-list {
  margin-top: 30px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  margin-bottom: 20px;
  transition: all 0.3s;
}

.history-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.history-content {
  flex: 1;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.edit-title {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.history-title {
  font-size: 18px;
  margin: 0;
  color: #333;
}

.history-date {
  font-size: 14px;
  color: #999;
}

.history-tags {
  margin-bottom: 10px;
}

.tag {
  margin-right: 8px;
}

.history-preview {
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.history-actions {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  margin-left: 20px;
}

.continue-btn {
  margin-bottom: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.save-btn {
  margin-left: 10px;
}

.edit-btn,
.delete-btn {
  font-size: 16px;
}

.edit-btn:hover {
  color: #409EFF;
}

.delete-btn:hover {
  color: #F56C6C;
}
</style> 