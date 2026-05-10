
document.addEventListener('DOMContentLoaded', function() {
  let selectedRole = 'student';
  
  
  document.addEventListener('click', function(e) {
    console.log('[DEBUG] Click event triggered on:', e.target);
    
    const roleTab = e.target.closest('.role-tab');
    if (roleTab) {
      const roleTabs = document.querySelectorAll('.role-tab');
      roleTabs.forEach(t => t.classList.remove('active'));
      roleTab.classList.add('active');
      
      
      if (roleTab.querySelector('i.fa-user-graduate')) selectedRole = 'student';
      else if (roleTab.querySelector('i.fa-chalkboard-teacher')) selectedRole = 'teacher';
      else if (roleTab.querySelector('i.fa-user-tie')) selectedRole = 'counselor';
      else if (roleTab.querySelector('i.fa-user-shield')) selectedRole = 'admin';
      console.log('[DEBUG] Selected role:', selectedRole);
    }
    
    
    const loginBtn = e.target.closest('#loginBtn');
    if (loginBtn) {
      console.log('[DEBUG] Login button clicked');
      handleLogin();
    }
  });
  
  
  document.addEventListener('submit', function(e) {
    const loginForm = e.target.closest('.login-form');
    if (loginForm) {
      e.preventDefault();
      handleLogin();
    }
  });
  
  
  async function handleLogin() {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginBtn = document.getElementById('loginBtn');
    const loadingIcon = document.getElementById('loadingIcon');
    const loginText = document.getElementById('loginText');
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!usernameInput || !passwordInput || !loginBtn) {
      console.error('Login elements not found');
      return;
    }
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    if (!username || !password) {
      showToast('请输入账号和密码', 'warning');
      return;
    }
    
    
    loginBtn.disabled = true;
    if (loadingIcon) loadingIcon.style.display = 'inline';
    if (loginText) loginText.textContent = '登录中...';
    
    try {
      console.log('Attempting login with:', username, selectedRole);
      
      const response = await fetch(window.location.origin + '/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      const data = await response.json();
      
      if (response.ok && data.access_token) {
        
        document.cookie = `ai_edu_token=${data.access_token}; path=/; SameSite=Lax`;
        document.cookie = `ai_edu_user=${encodeURIComponent(JSON.stringify(data.user))}; path=/; SameSite=Lax`;
        
        
        try {
          sessionStorage.setItem('ai_edu_token', data.access_token);
          sessionStorage.setItem('ai_edu_user', JSON.stringify(data.user));
        } catch (e) {
          console.warn('sessionStorage blocked');
        }
        
        showToast('登录成功！正在跳转...', 'success');
        
        
        setTimeout(() => {
          window.location.href = '/' + data.user.role + '/dashboard';
        }, 500);
      } else {
        showToast(data.detail || data.message || '登录失败', 'error');
      }
    } catch (error) {
      console.error('Login error:', error);
      showToast('登录失败：网络错误', 'error');
    } finally {
      
      loginBtn.disabled = false;
      if (loadingIcon) loadingIcon.style.display = 'none';
      if (loginText) loginText.textContent = '登 录';
    }
  }
  
  
  function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast || !toastIcon || !toastMessage) return;
    
    const icons = {
      success: 'fas fa-check-circle',
      error: 'fas fa-times-circle',
      warning: 'fas fa-exclamation-circle',
      info: 'fas fa-info-circle'
    };
    toastIcon.className = icons[type] || icons.info;
    toastMessage.textContent = message;
    toast.className = 'toast toast-' + type;
    toast.style.display = 'block';
    setTimeout(() => {
      toast.style.display = 'none';
    }, 3000);
  }
  
  console.log('Login handler initialized');
});