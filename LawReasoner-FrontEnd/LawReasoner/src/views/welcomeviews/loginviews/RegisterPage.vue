<script setup>
import { onBeforeUnmount, reactive, ref} from "vue";
import { User, Message, Lock, Clock, ArrowRight } from "@element-plus/icons-vue"
import router from "@/router/index.js";
import {postWithToken} from "@/axios/index.js"
import {ElMessage} from "element-plus";
import axios from "axios";
import {validateCode, validateEmail, validatePassword, validateUsername} from "@/validate/index.js";
import BackToHome from '@/components/BackToHome.vue';

const BASE_URL = "http://localhost:8000"

const formRef = ref()
const form = reactive({
  username: '',
  password: '',
  password_repeat: '',
  email: '',
  verification_code: ''
})

// 倒计时状态管理
const countdown = ref(60)
const isCountdown = ref(false)
let timer = null

const validatePassword_repeat = (rule, value, callback) => {
  if (value === ''){
    callback(new Error('请再次输入密码进行确认'))
  }
  else if (value !== form.password){
    callback(new Error('两次输入的密码不一致'))
  }
  else {
    callback()
  }
}


const rule = {
  username: [
    { validator: validateUsername, trigger: ['blur', 'change'] },
  ],
  password: [
    { validator: validatePassword, trigger: ['blur', 'change'] },
  ],
  password_repeat: [
    { validator: validatePassword_repeat, trigger: ['blur', 'change'] },
  ],
  email: [
    { validator: validateEmail, trigger: ['blur', 'change'] },
  ],
  verification_code: [
    { validator: validateCode, trigger: ['blur', 'change'] },
  ]
}

// 改进后的askForCode函数
function askForCode() {
  // 如果正在倒计时，直接返回
  if (isCountdown.value) return
  
  // 邮箱格式验证
  if(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(form.email)) {
    // 禁用按钮，开始倒计时
    isCountdown.value = true
    countdown.value = 60
    
    // 开始计时器
    timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
        isCountdown.value = false
      }
    }, 1000)
    
    // 发送请求
    axios.post(`${BASE_URL}/api/v1/register/send-code`, {
      email: form.email
    }, {
      headers: {
        "content-type": "application/json",
        "ngrok-skip-browser-warning": "true"
      }
    }).then(({data}) => {
      if (data.code === 200){
        ElMessage.success(`验证码已发送至邮箱地址：${form.email}`)
      }
      else {
        console.warn(`请求地址：/api/v1/reset-password/send-code，状态码：${data.code}，错误信息：${data.message}`)
        ElMessage.warning(data.data.detail)
      }
    })
    .catch(err => {
      // 出错时终止倒计时
      clearInterval(timer)
      isCountdown.value = false
      countdown.value = 60
      console.error('完整错误信息:', err)  // 添加更详细的错误日志
      if (err.response) {
        // 处理后端返回的错误
        const errorMsg = err.response.data.detail || '验证码发送失败'
        ElMessage.error(errorMsg)
        console.warn(`错误状态码：${err.response.status}，错误信息：${errorMsg}`)
      } else {
        // 处理网络错误
        console.warn(err)
        ElMessage.error('网络错误，请稍后重试')
      }
    })
  } else {
    ElMessage.warning('请输入正确的电子邮件')
  }
}

// 组件卸载时清理定时器
onBeforeUnmount(() => {
  if (timer) {
    clearInterval(timer)
  }
})

function register() {
  formRef.value.validate((valid) => {
    if(valid){
      axios.post(`${BASE_URL}/api/v1/register`, {
        username: form.username,
        password: form.password,
        email: form.email,
        verification_code: form.verification_code
      }, {
        headers: {
          "content-type": "application/json",
          "ngrok-skip-browser-warning": "true"
        }
      }).then(({data}) => {
        if (data.code === 200){
          ElMessage.success('注册成功，请尝试登录')
          router.push('/')
        }
        else {
          console.warn(`请求地址：/api/v1/register，状态码：${data.code}，错误信息：${data.message}`)
          ElMessage.warning(data.message)
        }
      }).catch(err => {
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
      })
    }
    else{
      ElMessage.warning('请完善表单内容')
    }
  })
}

function sendCode() {
  if (!form.email) {
    ElMessage.warning('请输入邮箱')
    return
  }
  axios.post(`${BASE_URL}/api/v1/register/send-code`, {
    email: form.email
  }, {
    headers: {
      "content-type": "application/json",
      "ngrok-skip-browser-warning": "true"
    }
  }).then(({data}) => {
    if (data.code === 200) {
      ElMessage.success('验证码已发送')
      countdown()
    } else {
      ElMessage.warning(data.message)
    }
  }).catch(err => {
    console.warn(err)
    ElMessage.warning('发送验证码失败')
  })
}

</script>

<template>
  <div style="text-align: center;margin: 20px 20px">
    <div style="margin-top: 50px">
      <div style="font-size: 25px;font-weight: bold">注册</div>
    </div>
    <div style="margin-top: 50px">
      <el-form :model="form" :rules="rule" ref="formRef">
        <el-form-item prop="username">
          <el-input v-model="form.username" maxlength="10" type="text" placeholder="用户名">
            <template #prefix>
              <el-icon><User/></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="form.password" maxlength="20" type="password" placeholder="密码">
            <template #prefix>
              <el-icon><Lock/></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password_repeat">
          <el-input v-model="form.password_repeat" maxlength="20" type="password" placeholder="再次输入确认密码">
            <template #prefix>
              <el-icon><Lock/></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="email">
          <el-input v-model="form.email" type="text" placeholder="电子邮件地址">
            <template #prefix>
              <el-icon><Message/></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="code">
          <el-row gutter="10" style="width: 80%">
            <el-col :span="17">
              <el-input v-model="form.verification_code" maxlength="6" type="text" placeholder="请输入验证码">
                <template #prefix>
                  <el-icon><Clock/></el-icon>
                </template>
              </el-input>
            </el-col>

            <el-col :span="5">
              <el-button @click="askForCode" type="success" plain :disabled="isCountdown" :loading="isCountdown">{{ isCountdown ? `${countdown}秒后重试` : '获取验证码' }}</el-button>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
    </div>
    <div style="margin-top: 50px">
      <el-button  @click="register" style="width: 250px" type="warning" plain>立即注册</el-button>
    </div>
    <div style="margin-top: 20px">
      <span style="font-size: 14px;line-height: 15px;color: grey">已有账号？</span>
      <el-link style="translate: 0 -1px" @click="router.push('/welcome')">立即登录</el-link>
    </div>
    <BackToHome />
  </div>
</template>

<style scoped>

</style>