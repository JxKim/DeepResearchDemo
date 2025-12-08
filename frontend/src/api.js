import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 10000,
});

// 请求拦截器：添加认证令牌
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取令牌
    const token = localStorage.getItem('token');
    if (token) {
      // 添加Authorization头
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // 处理请求错误
    return Promise.reject(error);
  }
);

// 响应拦截器：处理令牌过期或无效
api.interceptors.response.use(
  (response) => {
    // 2xx范围内的状态码都会触发该函数
    return response;
  },
  (error) => {
    // 非2xx范围内的状态码都会触发该函数
    if (error.response) {
      // 服务器返回了错误响应
      if (error.response.status === 401) {
        // 令牌过期或无效，清除本地存储并跳转到登录页面
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        // 刷新页面或跳转到登录页
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
