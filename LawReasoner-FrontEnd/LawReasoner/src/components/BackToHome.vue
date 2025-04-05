<script setup>
import { useRouter } from 'vue-router';
import { House } from '@element-plus/icons-vue';

const router = useRouter();

const goToHome = () => {
  router.push('/');
};
</script>

<template>
  <el-button 
    class="back-to-home" 
    type="primary" 
    plain 
    @click="goToHome"
  >
    <el-icon><House /></el-icon>
    返回首页
  </el-button>
</template>

<style scoped>
.back-to-home {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 100;
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 12px 20px;
  border-radius: 25px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.back-to-home:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0,0,0,0.15);
}

@media (max-width: 768px) {
  .back-to-home {
    bottom: 20px;
    right: 20px;
    padding: 10px 16px;
  }
}
</style> 