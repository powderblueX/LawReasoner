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

    // 添加调试日志
    console.log(`发送GET请求到: ${url}`);

    axios.get(url, {
        headers: header
    }).then(({data}) => {
        console.log(`接收到GET响应，URL: ${url}, 数据:`, data);

        // 特殊处理会话相关接口
        if (url.includes('/sessions')) {
            console.log('会话相关接口返回数据:', data);
            
            // 处理会话列表接口
            if (url.endsWith('/sessions')) {
                if (data.code === 200) {
                    console.log('会话列表接口返回成功状态');
                    
                    // 判断各种可能的数据结构
                    if (data.data && data.data.sessions) {
                        console.log('会话数据在 data.data.sessions 中');
                        success(data.data.sessions);
                        return;
                    } 
                    else if (data.data && Array.isArray(data.data)) {
                        console.log('会话数据直接在 data.data 数组中');
                        success(data.data);
                        return;
                    }
                    else if (data.sessions) {
                        console.log('会话数据在 data.sessions 中');
                        success(data.sessions);
                        return;
                    }
                    else if (Array.isArray(data)) {
                        console.log('会话数据直接是数组');
                        success(data);
                        return;
                    }
                    // 默认情况，返回整个data
                    console.log('使用默认数据结构');
                    success(data.data || data);
                    return;
                } else {
                    // 处理错误
                    console.warn('会话列表接口返回错误状态:', data.code, data.message);
                    ElMessage.warning(data.message || '加载会话列表失败');
                    success({ error: true, message: data.message || '加载会话列表失败' });
                    return;
                }
            }
            
            // 处理会话消息接口
            if (url.includes('/messages')) {
                console.log('会话消息接口返回');
                
                if (data.code === 200) {
                    if (data.data && data.data.messages) {
                        console.log('消息数据在 data.data.messages 中');
                        success(data.data);
                        return;
                    } 
                    else if (data.messages) {
                        console.log('消息数据在 data.messages 中');
                        success(data);
                        return;
                    }
                    // 默认情况
                    success(data.data || data);
                    return;
                } else {
                    console.warn('会话消息接口返回错误状态:', data.code, data.message);
                    success({ error: true, message: data.message || '加载会话消息失败' });
                    return;
                }
            }
        }

        // 默认处理
        if(data.code === 200){  // 服务器处理成功
            success(data.data)
        }
        else{   // 服务器处理失败
            console.warn(`请求地址：${url}，状态码：${data.code}，错误信息：${data.message}`)
            ElMessage.warning(data.message)
            
            // 返回错误对象，便于前端处理
            success({ error: true, message: data.message })
        }
    }).catch(err => {  // 连接失败
        console.warn(`请求失败: ${url}`, err)
        ElMessage.warning('发生了一些错误，请联系管理员')
        
        // 返回错误对象，便于前端处理
        success({ error: true, message: '网络连接失败' })
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

    console.log(`发送POST请求到: ${url}，携带数据:`, data);

    axios.post(url, data, {
        headers: header
    }).then(({data: responseData}) => {
        console.log(`接收到响应，原始数据:`, responseData);

        // 检查是否有嵌套的data字段
        let processedData = responseData;
        
        // 特殊处理聊天接口
        if (url.includes('/chat')) {
            if (responseData.code === 200 && responseData.data) {
                console.log('处理成功的聊天接口响应:', responseData.data);
                
                // 检查是否包含session_id
                if (responseData.data.session_id) {
                    console.log('检测到会话ID:', responseData.data.session_id);
                } else {
                    console.warn('响应中缺少会话ID，所有字段:', Object.keys(responseData.data));
                }
                
                // 检查响应内容中是否包含HTML标签
                const response = responseData.data.response || '';
                if (response && typeof response === 'string') {
                    const hasHtml = response.includes('<') && response.includes('>');
                    console.log(`响应长度: ${response.length}, 是否包含HTML: ${hasHtml}`);
                    
                    if (hasHtml) {
                        console.log('HTML响应片段:', response.substring(0, 100) + '...');
                    }
                }
                
                success(responseData.data);
                return;
            } else if (responseData.code !== 200 && responseData.data) {
                console.warn('处理失败的聊天接口响应:', responseData.data);
                ElMessage.warning(responseData.message || '请求处理失败');
                success(responseData.data); // 仍然传递data以便UI恢复
                return;
            }
        }

        // 常规处理
        if(responseData.code === 200){
            // 服务器处理成功
            if (responseData.data) {
                console.log('成功响应有data字段:', responseData.data);
                success(responseData.data);
            } else {
                console.log('成功响应无data字段，返回完整响应');
                success(responseData);
            }
        } else {
            // 服务器处理失败但返回了响应
            console.warn(`请求地址：${url}，状态码：${responseData.code}，错误信息：${responseData.message}`);
            
            // 显示错误消息
            const errorMessage = responseData.message || '请求处理失败';
            ElMessage.warning(errorMessage);
            
            // 调用回调以便UI恢复
            success({ error: true, message: errorMessage });
        }
    }).catch(err => {  // 连接失败
        console.warn(`请求失败: ${url}`, err);
        ElMessage.warning('发生了一些错误，请稍后重试');
        
        // 传入错误信息作为响应，以便UI恢复
        success({
            error: true,
            message: '网络连接失败，请检查网络并稍后重试'
        });
    });
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