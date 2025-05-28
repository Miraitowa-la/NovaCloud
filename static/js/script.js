/**
 * NovaCloud 全局 JavaScript
 */

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 主题切换功能
    initThemeToggle();
});

/**
 * 初始化主题切换功能
 */
function initThemeToggle() {
    // 获取页面body元素
    const body = document.getElementById('page-body');
    
    // 获取主题切换按钮（如果存在）
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    // 如果按钮不存在，返回
    if (!themeToggleBtn) return;
    
    /**
     * 设置主题
     * @param {string} theme - 'dark' 或 'light'
     */
    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            
            // 更新按钮图标为太阳（表示点击后切换到浅色模式）
            if (themeToggleBtn.querySelector('i')) {
                themeToggleBtn.querySelector('i').className = 'fas fa-sun';
            }
        } else {
            body.classList.remove('dark-mode');
            
            // 更新按钮图标为月亮（表示点击后切换到暗色模式）
            if (themeToggleBtn.querySelector('i')) {
                themeToggleBtn.querySelector('i').className = 'fas fa-moon';
            }
        }
        
        // 保存主题偏好到localStorage
        localStorage.setItem('theme', theme);
    }
    
    // 读取用户已保存的主题偏好
    const savedTheme = localStorage.getItem('theme');
    
    // 如果用户有保存的主题偏好，使用它
    if (savedTheme) {
        setTheme(savedTheme);
    } 
    // 否则，检测操作系统的主题偏好
    else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark');
    } 
    // 默认使用浅色主题
    else {
        setTheme('light');
    }
    
    // 监听主题切换按钮点击事件
    themeToggleBtn.addEventListener('click', function() {
        // 切换主题
        const currentTheme = localStorage.getItem('theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });
    
    // 监听操作系统主题变化（仅当用户未手动设置主题时响应）
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // 只有当用户没有手动设置过主题时，才跟随系统主题变化
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
} 