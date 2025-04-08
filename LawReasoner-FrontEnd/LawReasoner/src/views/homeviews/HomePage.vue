<script setup>
import { useRouter } from 'vue-router';
import { getToken } from '@/axios/index.js';
import { ElMessage } from 'element-plus';

const router = useRouter();

const goToContract = () => {
  router.push('/contract');
};

const goToChat = () => {
  router.push('/chat');
};

const goToLogIn = () => {
  // 检查用户是否已登录
  const token = getToken();
  if (token) {
    // 已登录，显示提示信息
    ElMessage({
      message: '您已登录，若要切换账号请在个人中心退出当前帐号',
      type: 'warning'
    });
  } else {
    // 未登录，跳转到登录页面
    router.push('/welcome');
  }
};

const goToProfile = () => {
  router.push('/profile');
};
</script>

<template>
  <div class="welcome-container">
    <!-- 导航栏 -->
    <nav class="welcome-nav">
      <div class="nav-left">
        <img class="avatar" src="@/assets/images/LawReasoner.png" alt="avatar">
        <span class="nav-logo">法理智推</span>
      </div>
      <div class="nav-right">
        <button class="nav-button" @click="goToLogIn">登录/注册</button>
        <button class="nav-button" @click="goToProfile">个人中心</button>
        <button class="nav-button" @click="goToChat">开始咨询</button>
        <button class="nav-button" @click="goToContract">合同生成</button>
      </div>
    </nav>

    <!-- 页面内容 -->
    <div class="welcome-header">
      <h1 class="welcome-title">欢迎使用法理智推</h1>
      <p class="welcome-subtitle">智能法律推理系统，助力法律资源公平分配与效率提升</p>
    </div>

    <div class="welcome-content">
      <!-- 系统功能概述 -->
      <section class="welcome-section">
        <h2 class="section-title">系统功能概述</h2>
        <div class="section-content">
          <div class="card">
            <h3>智能法律咨询</h3>
            <p>基于大语言模型的民事法律智能咨询系统，分析案情并给出合理判决结果，提供多轮对话，支持会话管理。</p>
          </div>
          <div class="card">
            <h3>《民法典》知识库</h3>
            <p>提供完整的《民法典》条文查询与浏览，按章节分类展示，支持关键词搜索，快速定位相关法条。</p>
          </div>
          <div class="card">
            <h3>智能合同生成</h3>
            <p>基于用户对话描述，智能推荐合适的合同模板，支持多种常用合同类型，自动填写合同内容，生成专业法律文书。</p>
          </div>
        </div>
      </section>

      <!-- 法律领域痛点分析 -->
      <section class="welcome-section">
        <h2 class="section-title">法律领域痛点分析</h2>
        <div class="section-content">
          <div class="card">
            <h3>法律资源分配不均</h3>
            <p>80%律师集中于一线城市，基层法律服务资源匮乏。</p>
          </div>
          <div class="card">
            <h3>案件处理效率低下</h3>
            <p>基层法院平均案件处理周期超过60天，司法效率亟待提升。</p>
          </div>
          <div class="card">
            <h3>法律知识普及困难</h3>
            <p>《民法典》1260条法规，公众认知率不足15%。</p>
          </div>
        </div>
      </section>

      <!-- 技术突破机遇 -->
      <section class="welcome-section">
        <h2 class="section-title">技术突破机遇</h2>
        <div class="section-content">
          <div class="card">
            <h3>deepseek-r1 1.5B 模型</h3>
            <p>deepseek-r1 1.5B 模型展现法律推理潜力，为智能法律系统提供技术基础。</p>
          </div>
          <div class="card">
            <h3>检索增强生成（RAG）技术成熟</h3>
            <p>BGE模型中文语义理解准确率提升至89.7%，助力精准法律推理。</p>
          </div>
          <div class="card">
            <h3>政策支持</h3>
            <p>最高法《智慧法院建设规划》明确提出AI辅助审判要求：“构建面向各类用户的人工智能感知交互体系和以知识为中心的人工智能辅助决策体系”。</p>
          </div>
        </div>
      </section>

      <!-- 项目独特性 -->
      <section class="welcome-section">
        <h2 class="section-title">"法理智推"中智能法律咨询的独特性</h2>
        <div class="section-content">
          <div class="card">
            <h3>首个专注《民法典》的智能推理系统</h3>
            <p>以《民法典》为核心，提供精准法律推理服务。</p>
          </div>
          <div class="card">
            <h3>法律条文与判例双知识库协同机制</h3>
            <p>结合法律条文与真实判例，提升推理准确性。</p>
          </div>
          <div class="card">
            <h3>思维链（CoT）技术保障推理可解释性</h3>
            <p>通过思维链技术，确保推理过程透明、可解释。</p>
          </div>
        </div>
      </section>
    </div>

    <!-- 页脚 -->
    <div class="welcome-footer">
      <p>法理智推 —— 让法律更智能，让正义更高效</p>
      <div class="author-info">
        <h3>开发者信息</h3>
        <p>姓名：powderblueX、zhu mingcan</p>
        <p>邮箱：minshijibai@163.com</p>
        <p>地址：上海市嘉定区曹安公路4800号</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.welcome-container {
  padding: 2rem;
  background-color: #f8f9fa;
  font-family: 'Arial', sans-serif;
  color: #333;
}

/* 导航栏样式 */
.welcome-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2c3e50;
  color: #fff;
  border-radius: 10px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.nav-left {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.nav-logo {
  font-family: KaiTi;
  font-weight: bolder;
  font-size: xx-large;
}

.nav-right {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 40px;
}

.nav-button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  color: #2c3e50;
  background-color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.nav-button:hover {
  background-color: #f0f4f8;
  transform: translateY(-2px);
}

.welcome-header {
  text-align: center;
  margin-bottom: 2rem;
  animation: fadeIn 1s ease-in-out;
}

.welcome-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.welcome-subtitle {
  font-size: 1.2rem;
  color: #666;
}

.welcome-content {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  margin-bottom: 3rem;
  animation: slideIn 1s ease-in-out;
}

.section-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  text-align: center;
}

.section-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.card {
  background-color: #fff;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
}

.card h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.card p {
  font-size: 1rem;
  color: #666;
  line-height: 1.6;
}

.welcome-footer {
  text-align: center;
  margin-top: 3rem;
  padding: 1rem;
  background-color: #2c3e50;
  color: #fff;
  border-radius: 10px;
  animation: fadeIn 1s ease-in-out;
}

.author-info {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.author-info h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.author-info p {
  font-size: 0.9rem;
  margin: 0.3rem 0;
  color: #e0e0e0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
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
</style>