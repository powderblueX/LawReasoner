<script setup>
</script>

<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <h1 class="not-found-title">404</h1>
      <p class="not-found-message">Oops! 页面未找到</p>
      <p class="not-found-description">您访问的页面似乎不存在，可能已被移除或暂时不可用。</p>
      <router-link to="/" class="not-found-button">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f4f8;
  font-family: 'Arial', sans-serif;
}

.not-found-content {
  text-align: center;
  animation: fadeIn 1.5s ease-in-out;
}

.not-found-title {
  font-size: 8rem;
  color: #ff6b6b;
  margin: 0;
  animation: bounce 2s infinite;
}

.not-found-message {
  font-size: 2rem;
  color: #333;
  margin: 10px 0;
}

.not-found-description {
  font-size: 1rem;
  color: #666;
  margin: 10px 0 20px;
}

.not-found-button {
  padding: 10px 20px;
  font-size: 1rem;
  color: #fff;
  background-color: #ff6b6b;
  border: none;
  border-radius: 5px;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.not-found-button:hover {
  background-color: #ff4757;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-30px);
  }
  60% {
    transform: translateY(-15px);
  }
}
</style>