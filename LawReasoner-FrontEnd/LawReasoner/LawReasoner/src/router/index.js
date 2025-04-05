import {createRouter, createWebHistory} from "vue-router";
import {getRole, getToken} from "@/axios/index.js";
import ContractPage from '@/views/contractviews/ContractPage.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
      {
        path: "/",
        name: "main",
        component: () => import("@/views/MainView.vue"),
        children: [
          // 主页页面
          {
            path: "/",
            name: "home",
            component: () => import("@/views/homeviews/HomePage.vue"),
            meta: { title: "法理智推首页页面" },
          },

          // 登录、注册、密码重置页面
          {
            path: '/welcome',
            name: 'welcome',
            component: () => import('@/views/welcomeviews/WelcomeView.vue'),
            meta: { title: "法理智推页面" }, 
            children: [
              {
                  path: '',
                  name: 'welcome-login',
                  component: () => import('@/views/welcomeviews/loginviews/LoginPage.vue'),
                  meta: { title: "法理智推登录页面" }, 
              },
              {
                  path: '/register',
                  name: 'welcome-register',
                  component: () => import('@/views/welcomeviews/loginviews/RegisterPage.vue'),
                  meta: { title: "法理智推注册页面" }, 
              },
              {
                  path: '/reset',
                  name: 'welcome-reset',
                  component: () => import('@/views/welcomeviews/loginviews/ResetPage.vue'),
                  meta: { title: "法理智推密码重置页面" }, 
              }
            ]
          },
        
          // 对话页面
          {
            path: "/chat",
            name: "chat-main",
            component: () => import("@/views/chatviews/ChatMainView.vue"),
            meta: { title: "法理智推对话页面" }, 
            children: [
              // 对话页面
              {
                path: "",
                name: "chat",
                component: () => import("@/views/chatviews/chatviews/ChatPage.vue"),
                meta: { title: "法理智推对话页面" }, 
              },
              // 历史会话管理页面
              {
                path: "history",
                name: "history",
                component: () => import("@/views/chatviews/historyviews/HistoryPage.vue"),
                meta: { title: "法理智推历史会话" }, 
              },
              // 案例社区页面
              {
                path: "community",
                name: "community",
                component: () => import("@/views/chatviews/communityviews/CommunityPage.vue"),
                meta: { title: "法理智推案例社区" }, 
              },
              // 法律知识库页面
              {
                path: "knowledge",
                name: "knowledge",
                component: () => import("@/views/chatviews/knowledgeviews/KnowledgePage.vue"),
                meta: { title: "法理智推法律知识库" }, 
              },
              // // 法律文书生成页面
              // {
              //   path: "/document",
              //   name: "document",
              //   component: () => import("@/views/chatviews/documentviews/DocumentPage.vue"),
              //   meta: { title: "法理智推法律文书生成" }, 
              // },
            ]
          },

          // // 法律知识库页面
          // {
          //   path: "/knowledge",
          //   name: "knowledge",
          //   component: () => import("@/views/knowledgeviews/KnowledgePage.vue"),
          //   meta: { title: "法理智推法律知识库" }, 
          // },

          // // 历史会话管理页面
          // {
          //   path: "/history",
          //   name: "history",
          //   component: () => import("@/views/historyviews/HistoryPage.vue"),
          //   meta: { title: "法理智推历史会话" }, 
          // },

          // // 案例社区页面
          // {
          //   path: "/community",
          //   name: "community",
          //   component: () => import("@/views/communityviews/CommunityPage.vue"),
          //   meta: { title: "法理智推案例社区" }, 
          // },

          // 个人中心页面
          {
            path: "/profile",
            name: "profile",
            component: () => import("@/views/profileviews/ProfilePage.vue"),
            meta: { title: "法理智推个人中心" }, 
          },

          // 合同生成页面
          {
            path: '/contract',
            name: 'contract',
            component: ContractPage,
            meta: {
              requiresAuth: true,
              title: { title: "法理智推合同生成" }, 
            }
          },
        ],
      },
      // 404 页面
      {
        path: "/:pathMatch(.*)*",
        name: "not-found",
        component: () => import("@/views/notfoundviews/NotFoundPage.vue"),
        meta: { title: "页面未找到" },
      },
    ],
});

// 配置路由守卫
router.beforeEach((to, from, next) => {
    const token = getToken()
    
    // 已经登录后不能再访问登录界面
    // 选择记住密码后，token被存储在localStorage中
    // 下次登录是可以获取的，故不能再访问登录界面，直接重定向到主界面，完成记住密码的功能
    if(to.name.startsWith('welcome-') && token !== null) {
      let role = getRole()
      if (role === 'user'){
          next('/')  // 重定向
      }
      else if (role === 'admin'){
          next('/')
      }
    }

    // 在没登录的情况下访问用户界面或管理员界面，直接跳转到登录界面
    if((to.fullPath.startsWith('/chat') || to.fullPath.startsWith('/contract') || to.fullPath.startsWith('/profile')) && token === null){
        next('/welcome')  // 重定向
    }

    else {  // 正常情况下
        next()   // 无需重定向
    }

})

export default router

