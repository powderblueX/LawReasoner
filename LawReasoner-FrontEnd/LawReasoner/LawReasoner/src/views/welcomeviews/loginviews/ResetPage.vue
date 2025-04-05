<script setup>
import {reactive, ref} from "vue";
import {Clock, Lock, Message} from "@element-plus/icons-vue"
import {ElMessage} from "element-plus";
import router from "@/router/index.js";
import {validateCode, validateEmail, validatePassword} from "@/validate/index.js";
import BackToHome from '@/components/BackToHome.vue';
import axios from "axios";

// 当前的步骤
const formRef = ref()
const form = reactive({
  email: '',
  verification_code: '',
  new_password: '',
  new_password_repeat: ''
})

const validatePassword_repeat = (rule, value, callback) => {
  if (value === ''){
    callback(new Error('请再次输入密码进行确认'))
  }
  else if (value !== form.new_password){
    callback(new Error('两次输入的密码不一致'))
  }
  else {
    callback()
  }
}

const rule = {
  new_password: [
    { validator: validatePassword, trigger: ['blur', 'change'] },
  ],
  new_password_repeat: [
    { validator: validatePassword_repeat, trigger: ['blur', 'change'] },
  ],
  email: [
    { validator: validateEmail, trigger: ['blur', 'change'] },
  ],
  verification_code: [
    { validator: validateCode, trigger: ['blur', 'change'] },
  ]
}

function askForCode() {
  if(/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(form.email)){
    axios.post('/api/v1/reset-password/send-code',{
      email: form.email
    }).then(({data}) => {
      if (data.code === 200){
        ElMessage.success(`验证码已发送至邮箱地址：${form.email}`)
      }
      else {
        console.warn(`请求地址：/api/v1/reset-password/send-code，状态码：${data.code}，错误信息：${data.message}`)
        ElMessage.warning(data.message)
      }
    }).catch(err => {
      console.warn(err)
      ElMessage.warning('发生了一些错误，请联系管理员')
    })
  }else {
    ElMessage.warning('请输入正确的电子邮件')
  }
}

function resetPassword(){
  formRef.value.validate((valid) => {
    if (valid){
      axios.post('/api/v1/reset-password',{
        new_password: form.new_password,
        email: form.email,
        verification_code: form.verification_code
      }).then(({data}) => {
        if (data.code === 200){
          ElMessage.success('修改密码成功，请尝试登录')
          router.push('/')
        }
        else {
          console.warn(`请求地址：/api/v1/reset-password，状态码：${data.code}，错误信息：${data.message}`)
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

</script>

<template>
  <div style="text-align: center;margin: 20px 20px">
    <div style="margin-top: 50px">
      <div style="font-size: 25px;font-weight: bold">重置密码</div>
    </div>
    <div style="margin-top: 50px">
      <el-form :model="form"  :rules="rule" ref="formRef">
        <el-form-item prop="password">
          <el-input v-model="form.new_password" maxlength="20" type="password" placeholder="密码">
            <template #prefix>
              <el-icon><Lock/></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password_repeat">
          <el-input v-model="form.new_password_repeat" maxlength="20" type="password" placeholder="再次输入确认密码">
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
          <el-row gutter="10" style="width: 100%">
            <el-col :span="17">
              <el-input v-model="form.verification_code" maxlength="6" type="text" placeholder="请输入验证码">
                <template #prefix>
                  <el-icon><Clock/></el-icon>
                </template>
              </el-input>
            </el-col>

            <el-col :span="5">
              <el-button @click="askForCode" type="success" plain>获取验证码</el-button>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
    </div>
    <div style="margin-top: 50px">
      <el-button @click="resetPassword" style="width: 250px" type="warning" plain>重置密码</el-button>
    </div>
    <BackToHome />
  </div>
</template>

<style scoped>

</style>