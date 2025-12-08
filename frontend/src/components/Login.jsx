import { useState } from 'react';
import api from '../api';
import './Login.css';

const Login = ({ onLogin, onClose }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('请输入用户名和密码');
      return;
    }

    try {
      let response;
      if (isRegistering) {
        // 调用注册API
        response = await api.post('/auth/register', {
          username,
          password,
          email: `${username}@example.com`,
          full_name: username
        });
      } else {
        // 调用登录API
        response = await api.post('/auth/login', {
          username,
          password
        });
      }
      
      // 处理API响应
      const token = response.data.access_token;
      
      // 调用验证令牌API获取用户信息
      const verifyResponse = await api.post('/auth/verify', { token });
      
      // 构建用户数据
      const userData = {
        id: verifyResponse.data.data.id,
        username: verifyResponse.data.data.username,
        email: verifyResponse.data.data.email,
        full_name: verifyResponse.data.data.full_name,
        token: token
      };
      
      // 存储用户数据和令牌到localStorage
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('token', token);
      
      // 调用父组件的登录回调
      onLogin(userData);
      onClose();
    } catch (err) {
      // 打印完整的错误信息，方便调试
      console.error('认证失败:', err);
      console.error('错误配置:', {
        isRegistering: isRegistering,
        username: username,
        password: password
      });
      
      if (err.response) {
        // 服务器返回了响应
        console.error('响应状态:', err.response.status);
        console.error('响应头:', err.response.headers);
        console.error('响应数据:', err.response.data);
        
        // 处理不同的错误情况
        if (err.response.data.detail) {
          // FastAPI返回的错误格式
          setError(err.response.data.detail);
        } else if (err.response.data.message) {
          // 自定义返回的错误格式
          setError(err.response.data.message);
        } else {
          // 其他格式的错误
          setError(JSON.stringify(err.response.data));
        }
      } else if (err.request) {
        // 请求已发送但没有收到响应
        console.error('请求:', err.request);
        setError('服务器未响应，请检查网络连接');
      } else {
        // 请求配置错误
        console.error('请求配置错误:', err.message);
        setError('请求配置错误，请稍后重试');
      }
    }
  };

  return (
    <div className="login-overlay">
      <div className="login-modal">
        <button className="close-btn" onClick={onClose}></button>
        
        <div className="login-header">
          <h2>{isRegistering ? '用户注册' : '用户登录'}</h2>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="请输入用户名"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="请输入密码"
              autoComplete="current-password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn">
            {isRegistering ? '注册' : '登录'}
          </button>
        </form>

        <div className="login-footer">
          <button 
            type="button" 
            className="toggle-mode-btn"
            onClick={() => setIsRegistering(!isRegistering)}
          >
            {isRegistering ? '已有账号？登录' : '没有账号？注册'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;