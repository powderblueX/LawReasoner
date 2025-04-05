<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElButton, ElInput, ElTag, ElAvatar, ElDivider, ElDialog, ElMessage, ElTabs, ElTabPane } from 'element-plus';
import { Search, Plus, Message, View, Star, StarFilled, Share } from '@element-plus/icons-vue';
import router from '@/router';
import UserAvatar from '@/assets/images/UserAvatar.png';
// 案例列表
const caseList = ref([
  {
    id: 1,
    title: '小区物业拒绝提供服务，业主如何维权？',
    content: '我所在的小区最近发生了一件事情。物业公司以小区部分业主欠缴物业费为由...',
    tags: ['物业纠纷', '服务合同'],
    author: '法律咨询者',
    avatar: UserAvatar,
    date: '2023-09-20',
    views: 156,
    comments: 12,
    stars: 23,
    isStarred: false
  },
  {
    id: 2,
    title: '网购商品七天无理由退货被拒，如何解决？',
    content: '我在某电商平台购买了一件衣服，收到后发现不合适，想要退货。但商家以已拆封为由拒绝...',
    tags: ['消费者权益', '电子商务'],
    author: '消费者权益关注者',
    avatar: UserAvatar,
    date: '2023-09-15',
    views: 203,
    comments: 18,
    stars: 36,
    isStarred: true
  },
  {
    id: 3,
    title: '公司无故降薪，员工如何维护自己的权益？',
    content: '我在一家科技公司工作了3年，最近公司以业绩下滑为由，单方面通知降薪30%...',
    tags: ['劳动合同', '薪资纠纷'],
    author: '劳动法研究员',
    avatar: UserAvatar,
    date: '2023-09-10',
    views: 287,
    comments: 24,
    stars: 45,
    isStarred: false
  }
]);

// 搜索和筛选
const searchKeyword = ref('');
const activeTab = ref('all');

// 新建案例相关
const newCaseDialogVisible = ref(false);
const newCase = reactive({
  title: '',
  content: '',
  tags: []
});
const tagInput = ref('');

// 案例详情
const selectedCase = ref(null);
const caseDetailVisible = ref(false);

// 评论相关
const commentContent = ref('');
const comments = ref([
  {
    id: 1,
    author: '法律顾问',
    avatar: UserAvatar,
    content: '根据《消费者权益保护法》第二十五条规定，消费者在网购商品时享有7天无理由退货的权利。',
    date: '2023-09-16 10:45'
  },
  {
    id: 2,
    author: '资深律师',
    avatar: UserAvatar,
    content: '建议保留好聊天记录和购物凭证，可以向消费者协会投诉，或者直接向电商平台反映。',
    date: '2023-09-16 14:30'
  }
]);

// 筛选案例
const filteredCases = () => {
  return caseList.value.filter(item => {
    // 关键词搜索
    const keywordMatch = !searchKeyword.value || 
      item.title.includes(searchKeyword.value) || 
      item.content.includes(searchKeyword.value) ||
      item.tags.some(tag => tag.includes(searchKeyword.value));
    
    // 标签筛选
    const tabMatch = activeTab.value === 'all' || 
      (activeTab.value === 'starred' && item.isStarred);
    
    return keywordMatch && tabMatch;
  });
};

// 查看案例详情
const viewCaseDetail = (caseItem) => {
  selectedCase.value = caseItem;
  caseDetailVisible.value = true;
  // 增加浏览量
  const index = caseList.value.findIndex(item => item.id === caseItem.id);
  if (index !== -1) {
    caseList.value[index].views++;
  }
};

// 收藏/取消收藏
// const toggleStar = (caseItem) => {
//   const index = caseList.value.findIndex(item => item.id === caseItem.id);
//   if (index !== -1) {
//     const isStarred = caseList.value[index].isStarred;
//     caseList.value[index].isStarred = !isStarred;
    
//     if (isStarred) {
//       caseList.value[index].stars--;
//       ElMessage({
//         message: '已取消收藏',
//         type: 'info'
//       });
//     } else {
//       caseList.value[index].stars++;
//       ElMessage({
//         message: '收藏成功',
//         type: 'success'
//       });
//     }
//   }
// };

// 添加标签
const addTag = () => {
  if (tagInput.value && !newCase.tags.includes(tagInput.value)) {
    newCase.tags.push(tagInput.value);
    tagInput.value = '';
  }
};

// 移除标签
const removeTag = (tag) => {
  const index = newCase.tags.indexOf(tag);
  if (index !== -1) {
    newCase.tags.splice(index, 1);
  }
};

// 发布新案例
const publishCase = () => {
  if (!newCase.title.trim() || !newCase.content.trim()) {
    ElMessage.warning('标题和内容不能为空');
    return;
  }
  
  // 创建新案例
  const newCaseItem = {
    id: caseList.value.length + 1,
    title: newCase.title,
    content: newCase.content,
    tags: [...newCase.tags],
    author: '当前用户',
    avatar: UserAvatar,
    date: new Date().toISOString().split('T')[0],
    views: 0,
    comments: 0,
    stars: 0,
    isStarred: false
  };
  
  // 添加到列表
  caseList.value.unshift(newCaseItem);
  
  // 重置表单
  newCase.title = '';
  newCase.content = '';
  newCase.tags = [];
  
  // 关闭对话框
  newCaseDialogVisible.value = false;
  
  ElMessage({
    message: '发布成功',
    type: 'success'
  });
};

// 发布评论
const submitComment = () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('评论内容不能为空');
    return;
  }
  
  // 创建新评论
  const newComment = {
    id: comments.value.length + 1,
    author: '当前用户',
    avatar: UserAvatar,
    content: commentContent.value,
    date: new Date().toLocaleString()
  };
  
  // 添加到评论列表
  comments.value.push(newComment);
  
  // 增加评论数
  if (selectedCase.value) {
    const index = caseList.value.findIndex(item => item.id === selectedCase.value.id);
    if (index !== -1) {
      caseList.value[index].comments++;
      selectedCase.value.comments++;
    }
  }
  
  // 清空输入框
  commentContent.value = '';
  
  ElMessage({
    message: '评论成功',
    type: 'success'
  });
};

// 分享案例
const shareCase = (caseItem) => {
  // 模拟分享操作
  ElMessage({
    message: '分享链接已复制到剪贴板',
    type: 'success'
  });
};
</script>

<template>
  <div class="community-container">
    <h1 class="page-title">案例社区</h1>
    
    <div class="control-panel">
      <div class="search-box">
        <el-input 
          v-model="searchKeyword" 
          placeholder="搜索案例标题、内容或标签" 
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      
      <el-button 
        type="primary" 
        @click="newCaseDialogVisible = true"
        class="new-case-btn"
      >
        <el-icon><Plus /></el-icon> 发布新案例
      </el-button>
    </div>
    
    <el-tabs v-model="activeTab" class="case-tabs">
      <el-tab-pane label="全部案例" name="all"></el-tab-pane>
      <!-- <el-tab-pane label="我的收藏" name="starred"></el-tab-pane> -->
    </el-tabs>
    
    <div class="case-list">
      <div 
        v-for="caseItem in filteredCases()" 
        :key="caseItem.id"
        class="case-item"
      >
        <div class="case-header">
          <div class="case-title-container" @click="viewCaseDetail(caseItem)">
            <h2 class="case-title">{{ caseItem.title }}</h2>
          </div>
          
          <div class="case-author">
            <el-avatar :src="caseItem.avatar" size="small"></el-avatar>
            <span>{{ caseItem.author }}</span>
            <span class="case-date">{{ caseItem.date }}</span>
          </div>
        </div>
        
        <div class="case-tags">
          <el-tag 
            v-for="(tag, index) in caseItem.tags" 
            :key="index"
            size="small"
            effect="plain"
            class="tag"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <p class="case-content" @click="viewCaseDetail(caseItem)">{{ caseItem.content }}</p>
        
        <div class="case-footer">
          <!-- <div class="case-stats">
            <span class="stat">
              <el-icon><View /></el-icon> {{ caseItem.views }}
            </span>
            <span class="stat">
              <el-icon><Message /></el-icon> {{ caseItem.comments }}
            </span>
          </div> -->
          
          <!-- <div class="case-actions">
            <el-button type="text" @click="toggleStar(caseItem)" class="star-btn">
              <el-icon>
                <StarFilled v-if="caseItem.isStarred" />
                <Star v-else />
              </el-icon>
              {{ caseItem.stars }}
            </el-button>
            
            <el-button type="text" @click="shareCase(caseItem)" class="share-btn">
              <el-icon><Share /></el-icon> 分享
            </el-button>
          </div> -->
        </div>
      </div>
    </div>
    
    <!-- 案例详情对话框 -->
    <el-dialog 
      v-model="caseDetailVisible" 
      title="案例详情"
      width="70%"
      class="case-detail-dialog"
    >
      <div v-if="selectedCase" class="case-detail">
        <h1 class="detail-title">{{ selectedCase.title }}</h1>
        
        <div class="detail-author">
          <el-avatar :src="selectedCase.avatar"></el-avatar>
          <div class="author-info">
            <div class="author-name">{{ selectedCase.author }}</div>
            <div class="detail-date">{{ selectedCase.date }}</div>
          </div>
        </div>
        
        <div class="detail-tags">
          <el-tag 
            v-for="(tag, index) in selectedCase.tags" 
            :key="index"
            size="small"
            effect="plain"
            class="tag"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <div class="detail-content">
          {{ selectedCase.content }}
        </div>
        
        <!-- <div class="detail-actions">
          <el-button type="text" @click="toggleStar(selectedCase)">
            <el-icon>
              <StarFilled v-if="selectedCase.isStarred" />
              <Star v-else />
            </el-icon>
            收藏 ({{ selectedCase.stars }})
          </el-button>
          
          <el-button type="text" @click="shareCase(selectedCase)">
            <el-icon><Share /></el-icon> 分享
          </el-button>
        </div> -->
        
        <el-divider>评论 ({{ selectedCase.comments }})</el-divider>
        
        <div class="comments-section">
          <div 
            v-for="comment in comments" 
            :key="comment.id"
            class="comment-item"
          >
            <div class="comment-author">
              <el-avatar :src="comment.avatar" size="small"></el-avatar>
              <div>
                <div class="author-name">{{ comment.author }}</div>
                <div class="comment-date">{{ comment.date }}</div>
              </div>
            </div>
            <div class="comment-content">{{ comment.content }}</div>
          </div>
        </div>
        
        <div class="new-comment">
          <el-input
            v-model="commentContent"
            type="textarea"
            rows="3"
            placeholder="分享您的观点..."
            class="comment-input"
          ></el-input>
          <el-button type="primary" @click="submitComment" class="submit-comment">
            发表评论
          </el-button>
        </div>
      </div>
    </el-dialog>
    
    <!-- 发布新案例对话框 -->
    <el-dialog 
      v-model="newCaseDialogVisible" 
      title="发布新案例"
      width="60%"
    >
      <div class="new-case-form">
        <div class="form-item">
          <div class="form-label">标题</div>
          <el-input 
            v-model="newCase.title" 
            placeholder="请输入案例标题"
          ></el-input>
        </div>
        
        <div class="form-item">
          <div class="form-label">内容</div>
          <el-input 
            v-model="newCase.content" 
            type="textarea"
            rows="6"
            placeholder="请详细描述您的案例，包括背景、问题和您的疑问等"
          ></el-input>
        </div>
        
        <div class="form-item">
          <div class="form-label">标签</div>
          <div class="tag-input-container">
            <el-input 
              v-model="tagInput" 
              placeholder="输入标签并按 Enter 添加"
              @keyup.enter="addTag"
              class="tag-input"
            ></el-input>
            <el-button @click="addTag" class="add-tag-btn">添加</el-button>
          </div>
          
          <div class="tag-list">
            <el-tag 
              v-for="(tag, index) in newCase.tags" 
              :key="index"
              closable
              @close="removeTag(tag)"
              class="tag"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="newCaseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="publishCase">发布</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.community-container {
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

.control-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  margin-right: 20px;
}

.new-case-btn {
  display: flex;
  align-items: center;
  gap: 5px;
}

.case-tabs {
  margin-bottom: 20px;
}

.case-list {
  margin-top: 20px;
}

.case-item {
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  margin-bottom: 20px;
  transition: all 0.3s;
}

.case-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.case-title-container {
  cursor: pointer;
}

.case-title {
  font-size: 18px;
  margin: 0;
  color: #333;
}

.case-author {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.case-date {
  margin-left: 8px;
  color: #999;
}

.case-tags {
  margin-bottom: 10px;
}

.tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.case-content {
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  cursor: pointer;
}

.case-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 15px;
}

.case-stats {
  display: flex;
  gap: 15px;
  color: #999;
}

.stat {
  display: flex;
  align-items: center;
  gap: 5px;
}

.case-actions {
  display: flex;
  gap: 15px;
}

.star-btn,
.share-btn {
  display: flex;
  align-items: center;
  gap: 5px;
}

.star-btn:hover {
  color: #E6A23C;
}

.case-detail-dialog :deep(.el-dialog__body) {
  padding: 20px 30px;
}

.detail-title {
  font-size: 24px;
  margin-bottom: 20px;
  color: #333;
}

.detail-author {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 500;
}

.detail-date {
  font-size: 14px;
  color: #999;
}

.detail-tags {
  margin-bottom: 20px;
}

.detail-content {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 30px;
  white-space: pre-wrap;
}

.detail-actions {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.comments-section {
  margin-top: 20px;
}

.comment-item {
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.comment-author {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.comment-date {
  font-size: 12px;
  color: #999;
}

.comment-content {
  margin-left: 40px;
  line-height: 1.5;
}

.new-comment {
  position: relative;
  margin-top: 30px;
}

.comment-input {
  margin-bottom: 15px;
}

.submit-comment {
  margin: 10px;       /* 可根据需要添加一些间距 */
}

.new-case-form {
  padding: 0 20px;
}

.form-item {
  margin-bottom: 20px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 8px;
}

.tag-input-container {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.tag-input {
  flex: 1;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
</style> 