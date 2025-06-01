/**
 * NovaCloud 全局 JavaScript
 */

console.log('NovaCloud 全局脚本已加载');

// 全局变量
let toastContainer;
const defaultToastDuration = 3000;

// 等待DOM加载完成
document.addEventListener('DOMContentLoaded', function() {
    // 主题切换功能
    initThemeToggle();
    initToastContainer();
    
    // 为所有表单初始化验证
    document.querySelectorAll('form[data-validate="true"]').forEach(form => {
        initFormValidation(form);
    });
    
    // 初始化可折叠部分
    initCollapsibleSections();
});

/**
 * 初始化主题切换功能
 */
function initThemeToggle() {
    // 获取页面body元素
    const body = document.getElementById('page-body');
    const html = document.documentElement;
    
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
            html.classList.add('theme-dark');
            html.setAttribute('data-theme', 'dark');
            
            // 更新按钮图标为太阳（表示点击后切换到浅色模式）
            if (themeToggleBtn.querySelector('i')) {
                themeToggleBtn.querySelector('i').className = 'fas fa-sun';
            }
        } else {
            body.classList.remove('dark-mode');
            html.classList.remove('theme-dark');
            html.setAttribute('data-theme', 'light');
            
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
        // 检查当前主题
        const isCurrentlyDark = document.body.classList.contains('dark-mode') || 
                                document.documentElement.classList.contains('theme-dark') ||
                                document.documentElement.getAttribute('data-theme') === 'dark';
        
        // 切换主题
        setTheme(isCurrentlyDark ? 'light' : 'dark');
    });
    
    // 监听操作系统主题变化（仅当用户未手动设置主题时响应）
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        // 只有当用户没有手动设置过主题时，才跟随系统主题变化
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

// 初始化Toast容器
function initToastContainer() {
    // 检查是否已存在Toast容器
    if (document.querySelector('.toast-container')) {
        toastContainer = document.querySelector('.toast-container');
        return;
    }
    
    // 创建Toast容器
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
}

/**
 * 显示Toast通知
 * @param {string} message - 通知消息
 * @param {string} type - 通知类型（'success', 'error', 'warning', 'info'）
 * @param {number} duration - 通知显示时间，毫秒（设为0则不会自动关闭）
 * @returns {HTMLElement} 创建的Toast元素
 */
function showToast(message, type = 'success', duration = defaultToastDuration) {
    if (!toastContainer) {
        initToastContainer();
    }
    
    // 设置适当的图标
    let icon;
    switch (type) {
        case 'success':
            icon = '<i class="fas fa-check-circle"></i>';
            break;
        case 'error':
            icon = '<i class="fas fa-exclamation-circle"></i>';
            break;
        case 'warning':
            icon = '<i class="fas fa-exclamation-triangle"></i>';
            break;
        case 'info':
        default:
            icon = '<i class="fas fa-info-circle"></i>';
            break;
    }
    
    // 创建Toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-content">
            <p class="toast-message">${message}</p>
        </div>
        <button type="button" class="toast-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // 添加关闭按钮事件监听
    const closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeToast(toast);
        });
    }
    
    // 添加到容器并触发动画
    toastContainer.appendChild(toast);
    
    // 使用requestAnimationFrame确保DOM更新后再添加show类
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });
    
    // 设置自动关闭
    if (duration > 0) {
        setTimeout(() => {
            closeToast(toast);
        }, duration);
    }
    
    return toast;
}

/**
 * 关闭指定的Toast通知
 * @param {HTMLElement} toast - Toast元素
 */
function closeToast(toast) {
    if (!toast) return;
    
    // 添加hiding类触发淡出动画
    toast.classList.add('hiding');
    toast.classList.remove('show');
    
    // 动画结束后移除元素
    setTimeout(() => {
        if (toast && toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 300); // 与CSS中的transition时间匹配
}

/**
 * 设置按钮加载状态
 * @param {HTMLElement} button - 按钮元素
 * @param {boolean} isLoading - 是否显示加载状态
 * @param {string} loadingText - 加载中显示的文本，如果为null则保留原文本
 */
function setButtonLoading(button, isLoading, loadingText = null) {
    if (!button) return;
    
    const originalHtml = button.getAttribute('data-original-html');
    
    if (isLoading) {
        // 存储原始HTML
        if (!originalHtml) {
            button.setAttribute('data-original-html', button.innerHTML);
        }
        
        // 添加加载类
        button.classList.add('btn-loading');
        
        // 设置加载状态内容
        const spinnerSize = button.classList.contains('btn-sm') ? 'spinner-sm' : '';
        const displayText = loadingText || button.textContent;
        
        button.innerHTML = `
            <span class="btn-text">${displayText}</span>
            <div class="btn-loading-overlay">
                <div class="spinner ${spinnerSize}"></div>
            </div>
        `;
        
        // 禁用按钮
        button.disabled = true;
    } else {
        // 恢复原始状态
        if (originalHtml) {
            button.innerHTML = originalHtml;
        }
        
        // 移除加载类
        button.classList.remove('btn-loading');
        
        // 启用按钮
        button.disabled = false;
    }
}

/**
 * 序列化表单数据为对象
 * @param {HTMLFormElement} form - 要序列化的表单
 * @returns {Object} 表单数据对象
 */
function serializeForm(form) {
    if (!form || form.nodeName !== 'FORM') {
        return null;
    }
    
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    return data;
}

/**
 * 将表单转换为AJAX提交
 * @param {HTMLFormElement} form - 表单元素 
 * @param {Object} options - 配置选项
 * @param {Function} options.onSuccess - 成功回调
 * @param {Function} options.onError - 错误回调
 * @param {Boolean} options.resetOnSuccess - 成功后是否重置表单
 * @param {Boolean} options.scrollToTop - 成功后是否滚动到顶部
 * @param {String} options.successMessage - 成功消息
 * @param {String} options.errorMessage - 错误消息
 */
function ajaxifyForm(form, options = {}) {
    if (!form || form.nodeName !== 'FORM') return;
    
    const defaults = {
        onSuccess: null,
        onError: null,
        resetOnSuccess: false,
        scrollToTop: false,
        successMessage: '操作成功',
        errorMessage: '操作失败，请重试'
    };
    
    const settings = { ...defaults, ...options };
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const formData = new FormData(form);
        
        // 获取提交按钮并显示加载状态
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) {
            setButtonLoading(submitButton, true);
        }
        
        // 发送AJAX请求
        fetch(form.action, {
            method: form.method || 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误：${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // 成功处理
            if (settings.successMessage) {
                showToast(settings.successMessage, 'success');
            }
            
            if (settings.resetOnSuccess) {
                form.reset();
            }
            
            if (settings.scrollToTop) {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
            
            if (typeof settings.onSuccess === 'function') {
                settings.onSuccess(data);
            }
        })
        .catch(error => {
            // 错误处理
            console.error('表单提交错误:', error);
            
            if (settings.errorMessage) {
                showToast(settings.errorMessage, 'error');
            }
            
            if (typeof settings.onError === 'function') {
                settings.onError(error);
            }
        })
        .finally(() => {
            // 恢复按钮状态
            if (submitButton) {
                setButtonLoading(submitButton, false);
            }
        });
    });
}

/**
 * 初始化表单验证功能
 * @param {HTMLFormElement} form - 要初始化的表单
 */
function initFormValidation(form) {
    if (!form) return;
    
    // 获取所有输入元素
    const inputs = form.querySelectorAll('input, select, textarea');
    
    // 为每个输入元素添加验证事件
    inputs.forEach(input => {
        // 仅对非隐藏、非按钮类型的输入元素添加验证
        if (input.type !== 'hidden' && input.type !== 'button' && input.type !== 'submit' && input.type !== 'reset') {
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('input', function() {
                // 如果已经被标记为无效，则在输入时重新验证
                if (this.classList.contains('is-invalid')) {
                    validateInput(this);
                }
            });
        }
    });
    
    // 表单提交时验证所有字段
    form.addEventListener('submit', function(e) {
        let isValid = true;
        
        inputs.forEach(input => {
            if (input.type !== 'hidden' && input.type !== 'button' && input.type !== 'submit' && input.type !== 'reset') {
                if (!validateInput(input)) {
                    isValid = false;
                }
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            e.stopPropagation();
            
            // 滚动到第一个无效输入
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstInvalid.focus();
            }
        }
    });
}

/**
 * 验证单个输入元素
 * @param {HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement} input - 输入元素
 * @returns {boolean} 是否有效
 */
function validateInput(input) {
    // 如果元素被禁用或不可见，则跳过验证
    if (input.disabled || input.type === 'hidden' || (input.offsetParent === null && input.type !== 'hidden')) {
        return true;
    }
    
    let isValid = true;
    const value = input.value.trim();
    
    // 清除现有验证状态
    input.classList.remove('is-invalid', 'is-valid');
    
    // 获取验证消息元素，如果不存在则创建
    let feedbackEl = input.nextElementSibling;
    if (!feedbackEl || !feedbackEl.classList.contains('invalid-feedback')) {
        feedbackEl = document.createElement('div');
        feedbackEl.className = 'invalid-feedback';
        input.parentNode.insertBefore(feedbackEl, input.nextSibling);
    }
    
    // 检查必填
    if (input.required && value === '') {
        isValid = false;
        feedbackEl.textContent = '此字段不能为空';
    }
    // 检查邮箱格式
    else if (input.type === 'email' && value !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            feedbackEl.textContent = '请输入有效的电子邮件地址';
        }
    }
    // 检查URL格式
    else if (input.type === 'url' && value !== '') {
        try {
            new URL(value);
        } catch (e) {
            isValid = false;
            feedbackEl.textContent = '请输入有效的URL';
        }
    }
    // 检查数字范围
    else if (input.type === 'number' && value !== '') {
        const num = Number(value);
        if (isNaN(num)) {
            isValid = false;
            feedbackEl.textContent = '请输入有效的数字';
        } else {
            if (input.min !== '' && num < Number(input.min)) {
                isValid = false;
                feedbackEl.textContent = `不能小于 ${input.min}`;
            }
            if (input.max !== '' && num > Number(input.max)) {
                isValid = false;
                feedbackEl.textContent = `不能大于 ${input.max}`;
            }
        }
    }
    // 检查自定义正则表达式
    else if (input.pattern && value !== '') {
        const pattern = new RegExp(input.pattern);
        if (!pattern.test(value)) {
            isValid = false;
            feedbackEl.textContent = input.title || '请按照要求的格式输入';
        }
    }
    // 检查密码强度
    else if (input.type === 'password' && input.dataset.passwordStrength === 'true' && value !== '') {
        // 简单密码强度检查: 至少8位，包含字母和数字
        const strongPassword = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        if (!strongPassword.test(value)) {
            isValid = false;
            feedbackEl.textContent = '密码至少需要8位，且包含字母和数字';
        }
    }
    // 检查密码确认
    else if (input.type === 'password' && input.dataset.passwordConfirm) {
        const passwordInput = document.getElementById(input.dataset.passwordConfirm);
        if (passwordInput && value !== passwordInput.value) {
            isValid = false;
            feedbackEl.textContent = '两次输入的密码不匹配';
        }
    }
    
    // 应用验证结果
    if (isValid) {
        if (value !== '') {
            input.classList.add('is-valid');
        }
    } else {
        input.classList.add('is-invalid');
    }
    
    return isValid;
}

/**
 * 初始化可折叠部分
 */
function initCollapsibleSections() {
    const collapsibles = document.querySelectorAll('.collapsible-section');
    
    collapsibles.forEach(section => {
        const header = section.querySelector('.collapsible-header');
        const content = section.querySelector('.collapsible-content');
        
        if (header && content) {
            header.addEventListener('click', function() {
                // 切换展开状态
                content.classList.toggle('show');
                
                // 更新图标方向
                const icon = header.querySelector('.fa-chevron-down, .fa-chevron-up');
                if (icon) {
                    if (content.classList.contains('show')) {
                        icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
                    } else {
                        icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
                    }
                }
            });
        }
    });
} 