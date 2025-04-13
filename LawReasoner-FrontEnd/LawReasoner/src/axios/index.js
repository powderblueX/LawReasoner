import axios from 'axios'
import {ElMessage} from "element-plus";
import router from "@/router/index.js";


const tokenKey = 'access_token'

// 存储 token，根据参数 remember 决定存储位置
function saveToken(token, expire, role, remember){
    const obj = { token: token, expire: expire, role: role }
    const str = JSON.stringify(obj)
    if(remember){
        localStorage.setItem(tokenKey, str)
    }
    else{
        sessionStorage.setItem(tokenKey, str)
    }
}

// 清除 token，不用多考虑，两个地方都删
function removeToken(){
    localStorage.removeItem(tokenKey)
    sessionStorage.removeItem(tokenKey)
}

// 获取 token，只有 token 存在且有效的时候才返回正确的 token，否则返回 null
function getToken(){
    let str = localStorage.getItem(tokenKey)
    if(!str) str = sessionStorage.getItem(tokenKey)

    // 检查是否登录
    if(!str) return null

    // 检查登录是否过期
    const obj = JSON.parse(str)
    
    // // 输出调试信息，帮助诊断问题
    // console.log("Token object:", obj);
    // console.log("Current time:", new Date());
    
    // // 将秒级时间戳转换为毫秒级
    // const expireMs = obj.expire * 1000; 
    // console.log("Expire time:", new Date(expireMs));
    
    // 将 expire 转换为日期对象进行比较（秒转毫秒）
    const expireDate = new Date(obj.expire * 1000);
    const now = new Date();
    
    if(expireDate <= now){
        console.log("Token expired");
        removeToken()
        return null
    }

    return obj.token
}

// 获取用户角色
function getRole(){
    let str = localStorage.getItem(tokenKey)
    if(!str) str = sessionStorage.getItem(tokenKey)

    // 检查是否登录
    if(!str) return null

    // 只有登录不过期才返回对应的 role
    const obj = JSON.parse(str)
    
    // 将 expire 转换为日期对象进行比较（秒转毫秒）
    const expireDate = new Date(obj.expire * 1000);
    const now = new Date();
    
    if(expireDate <= now){
        removeToken()
        return null
    }
    return obj.role
}

// 封装 token 请求头
function getTokenHeader(){
    const token = getToken()
    if(!token) return null
    return { 'Authorization': `Bearer ${token}` }
}


// 封装普通的 GET 和 POST 请求
// 即需要添加 token 请求头，且 POST 请求发送的数据为 JSON 格式的
// 不满足上面的叙述的请求，需要额外写
// 当检测到 token 无效时，会跳转到登录界面，要求重新登录

// get 请求
function getWithToken(url, success){
    const header = getTokenHeader()
    if(!header){
        // token 无效，不能发送本次请求
        ElMessage.warning('登录状态过期，请重新登录')
        router.push('/')
        return
    }

    axios.get(url, {
        headers: header
    }).then(({data}) => {
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else{   // 服务器处理失败
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.message)
        }
    }).catch(err => {  // 连接失败
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
    })
}

// post 请求
function postWithToken(url, data, success){
    const header = getTokenHeader()
    if(!header){
        // token 无效，不能发送本次请求
        ElMessage.warning('登录状态过期，请重新登录')
        router.push('/')
        return
    }

    axios.post(url, data, {
        headers: header
    }).then(({data}) => {
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else if (data.code >= 40000){
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.data.detail)
        }
    }).catch(err => {  // 连接失败
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
    })
}

// 封装不需要 token 的 GET 请求和 POST 请求

// get 请求
function get(url, success){
    axios.get(url, {
        headers: { "Content-Type": "application/json" }
    }).then(({data}) => {
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else{   // 服务器处理失败
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.data.detail)
        }
    }).catch(err => {  // 连接失败
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
    })
}

// post 请求
function post(url, data, success){
    axios.post(url, data, {
        headers: { "Content-Type": "application/json" }
    }).then(({data}) => {
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else{   // 服务器处理失败
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.data.detail)
        }
    }).catch(err => {  // 连接失败
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
    })
}

// 使用 multipart/form-data 形式传输的数据
// 也携带 token
function postWithMultipart(url, data, success){
    const token = getToken()
    if(!token){
        // token 无效，不能发送本次请求
        ElMessage.warning('登录状态过期，请重新登录')
        router.push('/')
        return
    }

    axios.post(url, data, {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': "multipart/form-data"
        }
    }).then(({data}) => {
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else{   // 服务器处理失败
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.message)
        }
    }).catch(err => {  // 连接失败
        console.warn(err)
        ElMessage.warning('发生了一些错误，请联系管理员')
    })
}

export{ saveToken, postWithMultipart, removeToken, getToken, getRole, get, post, getWithToken, postWithToken }