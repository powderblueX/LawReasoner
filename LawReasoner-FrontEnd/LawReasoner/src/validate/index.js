// 用户名有效性检验
const validateUsername = (rule, value, callback) => {
    if(value === '') {
        callback(new Error('请输入用户名'))
    }
    else if (!/^[a-zA-Z0-9\u4e00-\u9fa5]+$/.test(value)){
        callback(new Error('用户名只能使用中文或英文字符'))
    }
    else if (value.length > 10) {
        callback(new Error('用户名不能超过10个字符'))
    }
    else {
        callback()
    }
}

// 邮箱有效性检验
const validateEmail = (rule, value, callback) => {
    if (value === ''){
        callback(new Error('请输入邮箱地址'))
    }
    else if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)){
        callback(new Error('请输入正确的邮箱地址'))
    }
    else {
        callback()
    }
}

// 密码有效性检验
const validatePassword = (rule, value, callback) => {
    if (value === ''){
        callback(new Error('请输入密码'))
    }
    else if (value.length < 6 || value.length > 20){
        callback(new Error('密码的长度必须在6-20之间'))
    }
    else {
        callback()
    }

}

// 验证码有效性检验
const validateCode = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请输入验证码'))
    }
    else if (!/^\d+$/.test(value) || value.length !== 6){
        callback(new Error('验证码为6位阿拉伯数字'))
    }
    else {
        callback()
    }
}

export {validateUsername, validateEmail, validatePassword, validateCode}