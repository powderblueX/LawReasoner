<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElTree, ElInput, ElButton, ElTabs, ElTabPane, ElCard } from 'element-plus';
import { Search, Document, ArrowRight } from '@element-plus/icons-vue';
import BackToHome from '@/components/BackToHome.vue';

// 知识库章节数据
const chapters = reactive([
  {
    label: '第一编 总则',
    children: [
      { label: '第一章 基本规定', content: '第一条 为了保护民事主体的合法权益...' },
      { label: '第二章 自然人', content: '第十三条 自然人从出生时起到死亡时止...' },
      // 更多章节...
    ]
  },
  {
    label: '第二编 物权',
    children: [
      { label: '第一章 一般规定', content: '第二百零五条 本编调整因物的归属和...' },
      { label: '第二章 所有权', content: '第二百四十条 所有权人对自己的不动产...' },
      // 更多章节...
    ]
  },
  // 更多编...
]);

// 搜索相关
const searchKeyword = ref('');
const searchResults = ref([]);

// 选中的条款内容
const selectedContent = ref('');
const selectedTitle = ref('');

// 搜索条款
const searchLaw = () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  
  // 这里应该调用后端API进行搜索，这里模拟一些结果
  searchResults.value = [
    { title: '第一百八十六条', content: '因正当防卫造成损害的，不承担民事责任...' },
    { title: '第一百八十七条', content: '因紧急避险造成损害的，由引起险情发生的人承担民事责任...' },
    // 更多搜索结果...
  ];
};

// 选择条款
const selectLaw = (title, content) => {
  selectedTitle.value = title;
  selectedContent.value = content;
};

// 节点点击事件
const handleNodeClick = (data) => {
  if (data.content) {
    selectedTitle.value = data.label;
    selectedContent.value = data.content;
  }
};

// 默认选中第一条
onMounted(() => {
  if (chapters[0].children && chapters[0].children[0]) {
    selectedTitle.value = chapters[0].children[0].label;
    selectedContent.value = chapters[0].children[0].content;
  }
});
</script>

<template>
  <div class="knowledge-container">
    <h1 class="page-title">民法典知识库</h1>
    
    <el-tabs type="border-card" class="knowledge-tabs">
      <el-tab-pane label="章节浏览">
        <div class="knowledge-content">
          <div class="knowledge-tree">
            <el-tree 
              :data="chapters" 
              :props="{ children: 'children', label: 'label' }"
              @node-click="handleNodeClick"
              default-expand-all
            />
          </div>
          <div class="knowledge-detail">
            <el-card class="law-content">
              <h2>{{ selectedTitle }}</h2>
              <p>{{ selectedContent }}</p>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="关键词搜索">
        <div class="search-section">
          <el-input 
            v-model="searchKeyword" 
            placeholder="输入关键词搜索相关法律条款" 
            class="search-input"
          >
            <template #append>
              <el-button :icon="Search" @click="searchLaw">搜索</el-button>
            </template>
          </el-input>
          
          <div class="search-results">
            <div 
              v-for="(result, index) in searchResults" 
              :key="index"
              class="search-result-item"
              @click="selectLaw(result.title, result.content)"
            >
              <h3>{{ result.title }}</h3>
              <p>{{ result.content.substring(0, 100) + '...' }}</p>
            </div>
            
            <div v-if="searchResults.length === 0 && searchKeyword" class="no-results">
              没有找到相关条款
            </div>
          </div>
          
          <el-card v-if="selectedContent" class="law-content">
            <h2>{{ selectedTitle }}</h2>
            <p>{{ selectedContent }}</p>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 添加返回首页按钮 -->
    <BackToHome />
  </div>
</template>

<style scoped>
.knowledge-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-family: 'KaiTi', serif;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.knowledge-tabs {
  min-height: 600px;
}

.knowledge-content {
  display: flex;
  height: 600px;
}

.knowledge-tree {
  width: 300px;
  overflow-y: auto;
  border-right: 1px solid #eee;
  padding-right: 15px;
}

.knowledge-detail {
  flex: 1;
  padding-left: 20px;
  overflow-y: auto;
}

.search-section {
  padding: 20px;
}

.search-input {
  margin-bottom: 20px;
}

.search-results {
  margin-bottom: 20px;
}

.search-result-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-result-item:hover {
  background-color: #f5f7fa;
}

.law-content {
  margin-top: 20px;
  font-family: 'KaiTi', serif;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #909399;
}
</style> 