<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElTabs, ElTabPane, ElAvatar, ElButton, ElForm, ElFormItem, ElInput, ElTag, ElProgress, ElDialog, ElMessageBox } from 'element-plus';
import { Star, ChatRound, Document, SwitchButton, ChatSquare } from '@element-plus/icons-vue';
import router from '@/router';
import UserAvatar from '@/assets/images/UserAvatar.png';
import BackToHome from '@/components/BackToHome.vue';
import { getWithToken, postWithToken, removeToken } from '@/axios/index.js';

// 用户信息
const userInfo = reactive({
  username: '加载中...',
  email: '加载中...',
  avatar: UserAvatar,
  registerDate: '加载中...',
});

// 常用功能
const frequentlyUsed = ref([
  { name: '法律咨询', icon: ChatRound, route: '/chat' },
  { name: '法律知识库', icon: Document, route: '/chat/knowledge' },
  { name: '案例社区', icon: Star, route: '/chat/community' },
  { name: '合同生成', icon: ChatSquare, route: '/contract' },
]);

// 账户设置表单
const accountForm = reactive({
  username: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 退出登录对话框
const logoutDialogVisible = ref(false);
const isSaving = ref(false);
const isChanging = ref(false);

// 获取用户信息
const getUserInfo = () => {
  getWithToken('/api/v1/profile/info', (data) => {
    userInfo.username = data.username;
    userInfo.email = data.email;
    userInfo.registerDate = data.register_date;
    accountForm.username = data.username;
  });
};

// 保存账户信息
const saveAccountInfo = () => {
  if (isSaving.value) return;

  if (!accountForm.username) {
    ElMessage.warning('用户名不能为空');
    return;
  }

  isSaving.value = true;
  const startTime = Date.now();

  postWithToken('/api/v1/profile/update', {
    username: accountForm.username
  }, (data) => {
    userInfo.username = accountForm.username;
    ElMessage.success('账户信息已更新');
  }, (error) => {

  });
  const remaining = Math.max(3000 - (Date.now() - startTime), 0);
  setTimeout(() => isSaving.value = false, remaining);
};

// 修改密码
const changePassword = () => {
  if (isChanging.value) return;

  if (!accountForm.currentPassword || !accountForm.newPassword || !accountForm.confirmPassword) {
    ElMessage.warning('所有密码字段都必须填写');
    return;
  }
  
  if (accountForm.newPassword !== accountForm.confirmPassword) {
    ElMessage.error('新密码和确认密码不一致');
    return;
  }
  
  isChanging.value = true;
  const startTime = Date.now();

  postWithToken('/api/v1/profile/password', {
    current_password: accountForm.currentPassword,
    new_password: accountForm.newPassword
  }, (data) => {
    ElMessage.success(data.message);
    accountForm.currentPassword = '';
    accountForm.newPassword = '';
    accountForm.confirmPassword = '';
  }, (error) => {
    
  });
  const remaining = Math.max(3000 - (Date.now() - startTime), 0);
  setTimeout(() => isChanging.value = false, remaining);
};

// 跳转到相应功能页面
const navigateTo = (route) => {
  router.push(route);
};

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    // 调用退出登录API
    postWithToken('/api/v1/logout', {}, () => {
      // 清除本地存储的登录信息
      removeToken();
      ElMessage.success('已退出登录');
      router.push('/');
    });
  }).catch(() => {
    // 取消退出
  });
};

// 页面加载时获取用户信息
onMounted(() => {
  getUserInfo();
});
</script>

<template>
  <div class="profile-container">
    <h1 class="page-title">个人中心</h1>
    
    <div class="profile-content">
      <div class="user-info-card">
        <div class="avatar-section">
          <el-avatar :src="userInfo.avatar" :size="100"></el-avatar>
        </div>
        
        <div class="user-details">
          <h2>{{ userInfo.username }}</h2>
          <p class="user-email">{{ userInfo.email }}</p>
          <p class="join-date">注册时间：{{ userInfo.registerDate }}</p>
          
          <div class="stat-item">
            <div 
              v-for="(item, index) in frequentlyUsed" 
              :key="index"
              class="feature-card"
              @click="navigateTo(item.route)"
            >
              <el-icon :size="36"><component :is="item.icon" /></el-icon>
              <h3>{{ item.name }}</h3>
              <el-progress 
                :stroke-width="8" 
                :show-text="false"
              ></el-progress>
            </div>
          </div>
        </div>
      </div>
      
      <el-tabs type="border-card" class="profile-tabs">
        <!-- <el-tab-pane label="常用功能">
          <div class="frequently-used">
            <div 
              v-for="(item, index) in frequentlyUsed" 
              :key="index"
              class="feature-card"
              @click="navigateTo(item.route)"
            >
              <el-icon :size="36"><component :is="item.icon" /></el-icon>
              <h3>{{ item.name }}</h3>
              <p>使用次数: {{ item.count }}</p>
              <el-progress 
                :percentage="Math.min(100, item.count / 0.5)" 
                :stroke-width="8" 
                :show-text="false"
              ></el-progress>
            </div>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="我的收藏">
          <div class="favorites-list">
            <div 
              v-for="item in favorites" 
              :key="item.id"
              class="favorite-item"
            >
              <div class="favorite-info">
                <div class="favorite-header">
                  <div class="favorite-title">{{ item.title }}</div>
                  <el-tag size="small" effect="plain">{{ item.type }}</el-tag>
                </div>
                
                <div class="favorite-tags">
                  <el-tag 
                    v-for="(tag, index) in item.tags" 
                    :key="index"
                    size="small"
                    effect="light"
                    class="tag"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                
                <div class="favorite-date">收藏时间：{{ item.date }}</div>
              </div>
              
              <div class="favorite-actions">
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="navigateTo('/knowledge')"
                >
                  查看
                </el-button>
                
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeFavorite(item.id)"
                >
                  移除
                </el-button>
              </div>
            </div>
            
            <div v-if="favorites.length === 0" class="no-favorites">
              您还没有任何收藏
            </div>
          </div>
        </el-tab-pane> -->
        
        <el-tab-pane label="账户设置">
          <div class="account-settings">
            <h3>基本信息</h3>
            <el-form label-width="100px" class="account-form">
              <el-form-item label="用户名">
                <el-input v-model="accountForm.username"></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="saveAccountInfo" :disabled="isSaving">保存修改</el-button>
              </el-form-item>
            </el-form>
            
            <h3>修改密码</h3>
            <el-form label-width="100px" class="password-form">
              <el-form-item label="当前密码">
                <el-input 
                  v-model="accountForm.currentPassword" 
                  type="password"
                  show-password
                  placeholder="请输入当前密码"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="新密码">
                <el-input 
                  v-model="accountForm.newPassword" 
                  type="password"
                  show-password
                  placeholder="请输入新密码"
                ></el-input>
              </el-form-item>
              
              <el-form-item label="确认新密码">
                <el-input 
                  v-model="accountForm.confirmPassword" 
                  type="password"
                  show-password
                  placeholder="请再次输入新密码"
                ></el-input>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="changePassword" :disabled="isChanging">修改密码</el-button>
              </el-form-item>
            </el-form>

            <h3>账号安全</h3>
            <div class="security-settings">
              <div class="security-item">
                <div class="security-info">
                  <h4>退出登录</h4>
                  <p>退出当前账号，需要重新登录</p>
                </div>
                <el-button type="danger" @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <BackToHome />
  </div>
</template>

<style scoped>
.profile-container {
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

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.user-info-card {
  display: flex;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 30px;
}

.upload-btn {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.user-details {
  flex: 1;
}

.user-details h2 {
  margin-top: 0;
  margin-bottom: 5px;
  color: #333;
}

.user-email {
  color: #666;
  margin-bottom: 5px;
}

.join-date {
  color: #999;
  margin-bottom: 20px;
}

.stats {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-value {
  font-size: 20px;
  font-weight: 500;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.profile-tabs {
  margin-top: 20px;
}

.frequently-used {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  padding: 10px;
}

.feature-card {
  width: calc(33.333% - 20px);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.feature-card h3 {
  margin: 15px 0 10px 0;
  color: #333;
}

.feature-card p {
  color: #666;
  margin-bottom: 10px;
}

.favorites-list {
  padding: 10px;
}

.favorite-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  background-color: #fff;
}

.favorite-info {
  flex: 1;
}

.favorite-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.favorite-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.favorite-tags {
  margin-bottom: 10px;
}

.tag {
  margin-right: 8px;
}

.favorite-date {
  font-size: 14px;
  color: #999;
}

.favorite-actions {
  display: flex;
  gap: 10px;
}

.no-favorites {
  text-align: center;
  padding: 30px;
  color: #909399;
}

.account-settings {
  padding: 10px;
}

.account-settings h3 {
  margin-top: 20px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
  color: #333;
}

.account-form,
.password-form {
  max-width: 500px;
}

.security-settings {
  margin-top: 20px;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 10px;
}

.security-info h4 {
  margin: 0;
  color: #333;
}

.security-info p {
  margin: 5px 0 0;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .user-info-card {
    flex-direction: column;
    align-items: center;
  }
  
  .avatar-section {
    margin-right: 0;
    margin-bottom: 20px;
  }
  
  .user-details {
    text-align: center;
  }
  
  .stats {
    justify-content: center;
  }
  
  .feature-card {
    width: 100%;
  }
}
</style> 