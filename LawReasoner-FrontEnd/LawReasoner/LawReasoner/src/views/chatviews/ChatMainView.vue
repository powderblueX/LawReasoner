<script setup>

</script>

<template>
  <div>
    <router-view v-slot="{ Component }">
      <transition name="el-fade-in-linear" mode="out-in">
        <component :is="Component"/>
      </transition>
    </router-view>
  </div>
</template>

<style scoped>


</style>