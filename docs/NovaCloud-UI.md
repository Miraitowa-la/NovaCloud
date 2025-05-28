# NovaCloud UI 样式设计规范

## 1. 设计理念与原则

本 UI 样式规范旨在为 NovaCloud 物联网平台提供一套统一、美观、易用且具有现代感的前端视觉和交互标准。设计灵感来源于 GitHub，强调以下原则：

*   **清晰性 (Clarity)**：界面元素和信息层级清晰易懂，用户能快速找到所需功能。
*   **一致性 (Consistency)**：在整个平台中保持统一的视觉风格、交互模式和术语。
*   **效率 (Efficiency)**：优化用户操作路径，减少不必要的点击和认知负荷。
*   **响应式 (Responsive)**：确保在不同设备和屏幕尺寸上均有良好的用户体验。
*   **可访问性 (Accessibility)**：遵循 WCAG 标准，确保所有用户都能方便使用。
*   **现代感 (Modern)**：采用扁平化设计，配合微妙的阴影和过渡动画，营造专业可靠的视觉感受。

## 2. 核心元素

### 2.1 色彩规范

色彩系统基于 CSS 变量实现，方便主题管理和明暗模式切换。

**2.1.1 基础色板 (CSS 变量)**

```css
/* style.css - :root 部分 */
:root {
    /* 核心色调 - 浅色模式 */
    --color-primary: #3498db;         /* 主题蓝 (链接、强调按钮) */
    --color-primary-hover: #2980b9;   /* 主题蓝悬停 */
    --color-primary-active: #216a9a;  /* 主题蓝激活 */
    --color-secondary: #6c757d;       /* 次要灰 (辅助文本、次要按钮边框) */
    --color-secondary-hover: #5a6268; /* 次要灰悬停 */
    --color-success: #28a745;         /* 成功绿 */
    --color-danger: #dc3545;          /* 危险红 */
    --color-warning: #ffc107;         /* 警告黄 */
    --color-info: #17a2b8;            /* 信息蓝 */

    /* 背景色 - 浅色模式 */
    --background-body: #f6f8fa;       /* 页面背景 */
    --background-default: #ffffff;     /* 默认元素背景 (卡片、输入框) */
    --background-muted: #f1f3f5;       /* 轻微区分背景 (表格条纹、代码块) */
    --background-hover: #f8f9fa;       /* 悬停背景 */
    --background-selected: #e9ecef;    /* 选中背景 */

    /* 文本色 - 浅色模式 */
    --text-default: #24292f;          /* 主要文本 */
    --text-muted: #57606a;            /* 次要文本 (辅助信息、占位符) */
    --text-link: var(--color-primary); /* 链接文本 */
    --text-placeholder: #8b949e;      /* 输入框占位符 */
    --text-on-primary: #ffffff;       /* 主题色按钮上的文本 */
    --text-on-danger: #ffffff;        /* 危险色按钮上的文本 */

    /* 边框色 - 浅色模式 */
    --border-default: #d0d7de;        /* 默认边框 (输入框、卡片) */
    --border-muted: #e1e4e8;          /* 更浅的边框 (分隔线) */
    --border-focus: var(--color-primary); /* 焦点边框 */

    /* 阴影 */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.075);
    --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.1);

    /* 其他 */
    --border-radius-sm: 0.25rem; /* 4px */
    --border-radius-md: 0.375rem; /* 6px */
    --border-radius-lg: 0.5rem;  /* 8px */
}
```

#### **2.1.2 暗色模式覆盖 (CSS 变量)**

```css
/* style.css - body.dark-mode 部分 */
body.dark-mode {
    --color-primary: #58a6ff;
    --color-primary-hover: #79b8ff;
    --color-primary-active: #4191e1;
    --color-secondary: #8b949e;
    --color-secondary-hover: #a0aec0;
    --color-success: #3fb950;
    --color-danger: #f85149;
    --color-warning: #e3b341;
    --color-info: #58a6ff; /* 暗模式下信息色可与主色一致或稍作区分 */

    --background-body: #0d1117;
    --background-default: #161b22;
    --background-muted: #010409; /* 更深的背景，用于代码块或细微区分 */
    --background-hover: #222831;
    --background-selected: #2a3038;

    --text-default: #e6edf3;
    --text-muted: #7d8590;
    --text-link: var(--color-primary);
    --text-placeholder: #6e7681;
    --text-on-primary: #0d1117; /* 主题色按钮上用深色文字 */
    --text-on-danger: #ffffff;

    --border-default: #30363d;
    --border-muted: #21262d;
    --border-focus: var(--color-primary);

    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.15);
    --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.2);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
}
```

### 2.2 排版规范

#### **2.2.1 字体**

- **主字体栈**: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji"。优先使用系统默认字体，确保最佳性能和本地化体验。
- **代码字体栈**: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace。

#### **2.2.2 字号与行高**

```css
/* style.css */
body {
    font-family: var(--font-family-sans-serif); /* 在 :root 中定义 */
    font-size: 1rem; /* 默认为 16px */
    line-height: 1.6;
    color: var(--text-default);
    background-color: var(--background-body);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

h1, .h1 { font-size: 2rem; line-height: 1.2; margin-bottom: 0.75rem; font-weight: 600; }
h2, .h2 { font-size: 1.75rem; line-height: 1.25; margin-bottom: 0.6rem; font-weight: 600; }
h3, .h3 { font-size: 1.5rem; line-height: 1.3; margin-bottom: 0.5rem; font-weight: 600; }
h4, .h4 { font-size: 1.25rem; line-height: 1.35; margin-bottom: 0.4rem; font-weight: 600; }
h5, .h5 { font-size: 1.1rem; line-height: 1.4; margin-bottom: 0.3rem; font-weight: 600; }
h6, .h6 { font-size: 1rem; line-height: 1.4; margin-bottom: 0.25rem; font-weight: 600; }

p { margin-bottom: 1rem; }
a { color: var(--text-link); text-decoration: none; transition: color 0.15s ease-in-out; }
a:hover { color: var(--color-primary-hover); text-decoration: underline; }

small, .text-small { font-size: 0.875em; }
.text-muted { color: var(--text-muted) !important; }
```

在 :root 中定义字体族：

```css
:root {
    /* ... 其他变量 ... */
    --font-family-sans-serif: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    --font-family-monospace: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
}
```

### 2.3 图标系统 (Font Awesome 本地化)

使用 Font Awesome Free 版本，通过本地文件引入。

#### **2.3.1 文件结构**

```
static/
├── css/
│   ├── style.css
│   └── all.min.css  (核心样式文件)
├── js/
│   └── script.js
├── fonts/
├── webfonts/
│   ├── fa-brands-400.woff2
│   ├── fa-regular-400.woff2
│   ├── fa-solid-900.woff2
│   └── ... (其他字体文件)
└── index.html (或你的 Django 模板)
```

#### **2.3.2 HTML 引入**

在 HTML 的 <head> 标签中引入：

```html
<link rel="stylesheet" href="fonts/fontawesome/css/all.min.css">
<link rel="stylesheet" href="css/style.css">
```

#### **2.3.3 使用示例**

```html
<button class="btn btn-primary">
    <i class="fas fa-save"></i> 保存
</button>
<a href="#" class="nav-link"><i class="fas fa-tachometer-alt"></i> 仪表盘</a>
<span class="text-success"><i class="fas fa-check-circle"></i> 操作成功</span>
```

### 2.4 布局与间距

- **容器 (.container)**: 提供固定宽度的居中布局或流式布局。
- **网格系统**: (可选) 可引入简单的 Flexbox 或 CSS Grid 网格系统。
- **间距**: 使用 rem 单位，保持一致性。预定义一些 margin 和 padding 的辅助类 (如 .mt-1, .p-2 等，类似于 Bootstrap Spacing)。

```css
/* style.css */
.container {
    width: 100%;
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
}

@media (min-width: 576px) { .container { max-width: 540px; } }
@media (min-width: 768px) { .container { max-width: 720px; } }
@media (min-width: 992px) { .container { max-width: 960px; } }
@media (min-width: 1200px) { .container { max-width: 1140px; } }

/* 简易 Flex 辅助 */
.d-flex { display: flex !important; }
.align-items-center { align-items: center !important; }
.justify-content-between { justify-content: space-between !important; }
.justify-content-center { justify-content: center !important; }
.flex-grow-1 { flex-grow: 1 !important; }
```

## 3. 组件样式

### 3.1 按钮 (.btn)

按钮提供清晰的视觉反馈和操作指引。

```css
/* style.css */
.btn {
    display: inline-flex; /* 修改为 inline-flex 以便图标和文字垂直居中 */
    align-items: center;
    justify-content: center;
    font-weight: 500;
    line-height: 1.5;
    color: var(--text-default);
    text-align: center;
    vertical-align: middle;
    cursor: pointer;
    user-select: none;
    background-color: var(--background-default);
    border: 1px solid var(--border-default);
    padding: 0.5rem 1rem; /* 调整内边距以适应 GitHub 风格 */
    font-size: 0.875rem; /* 调整字体大小 */
    border-radius: var(--border-radius-md);
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn:hover {
    border-color: var(--border-muted); /* 调整悬停边框色 */
}

.btn:focus, .btn.focus {
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(var(--color-primary-rgb, 52, 152, 219), 0.25); /* 使用 RGB 变量 */
}
/* 在 :root 中添加 --color-primary-rgb */
:root { /* ... */ --color-primary-rgb: 52, 152, 219; }
body.dark-mode { /* ... */ --color-primary-rgb: 88, 166, 255; }


.btn:active, .btn.active {
    /* GitHub 风格的 active 状态通常是轻微的颜色变深或边框变化 */
}

.btn.disabled, .btn:disabled {
    opacity: 0.65;
    pointer-events: none;
}

/* 主按钮 */
.btn-primary {
    color: var(--text-on-primary);
    background-color: var(--color-primary);
    border-color: var(--color-primary);
}
.btn-primary:hover {
    color: var(--text-on-primary);
    background-color: var(--color-primary-hover);
    border-color: var(--color-primary-hover);
}
.btn-primary:active {
    color: var(--text-on-primary);
    background-color: var(--color-primary-active);
    border-color: var(--color-primary-active);
}


/* 次要按钮 (通常是默认样式，或略有不同) */
.btn-secondary {
    color: var(--text-default); /* 浅色模式下用深色文字，深色模式下用浅色文字 */
    background-color: var(--background-muted); /* 比默认按钮背景稍深或不同 */
    border-color: var(--border-default);
}
body.dark-mode .btn-secondary {
    color: var(--text-default);
}
.btn-secondary:hover {
    background-color: var(--background-selected); /* 悬停时颜色变化 */
    border-color: var(--border-muted);
}

/* 轮廓按钮 */
.btn-outline-primary {
    color: var(--color-primary);
    border-color: var(--color-primary);
    background-color: transparent;
}
.btn-outline-primary:hover {
    color: var(--text-on-primary);
    background-color: var(--color-primary);
    border-color: var(--color-primary);
}

/* 危险按钮 */
.btn-danger {
    color: var(--text-on-danger);
    background-color: var(--color-danger);
    border-color: var(--color-danger);
}
.btn-danger:hover {
    color: var(--text-on-danger);
    background-color: darken(var(--color-danger), 7.5%); /* 需要 JS 或 SCSS 辅助，或硬编码 */
    border-color: darken(var(--color-danger), 10%);
}
/* 简化: 直接指定悬停色 */
body:not(.dark-mode) .btn-danger:hover { background-color: #c82333; border-color: #bd2130; }
body.dark-mode .btn-danger:hover { background-color: #eA433c; border-color: #e0312a; }


/* 按钮尺寸 */
.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem; /* 更小字体 */
    border-radius: var(--border-radius-sm);
}
.btn-lg {
    padding: 0.65rem 1.25rem; /* 更大内边距 */
    font-size: 1rem; /* 标准字体或略大 */
    border-radius: var(--border-radius-md);
}

/* 带图标的按钮 */
.btn .fas, .btn .far, .btn .fab {
    margin-right: 0.5em; /* 图标和文字间距 */
    font-size: 0.9em; /* 图标略小于文字 */
}
.btn .fas:only-child, .btn .far:only-child, .btn .fab:only-child { /* 仅有图标的按钮 */
    margin-right: 0;
}
```

**HTML 示例**

```html
<button class="btn btn-primary"><i class="fas fa-rocket"></i> 启动</button>
<button class="btn btn-secondary">取消</button>
<button class="btn btn-outline-primary btn-sm">更多信息</button>
<button class="btn btn-danger btn-lg"><i class="fas fa-trash"></i> 删除</button>
<button class="btn btn-primary" disabled>处理中...</button>
```

### 3.2 导航栏 (.navbar)

**3.2.1 顶部导航栏**

```css
/* style.css */
.navbar {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    background-color: var(--background-default);
    border-bottom: 1px solid var(--border-muted);
    box-shadow: var(--shadow-sm);
    min-height: 60px;
}

.navbar-brand {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-default);
    margin-right: 1.5rem;
    text-decoration: none;
}
.navbar-brand:hover {
    color: var(--text-default);
    text-decoration: none;
}

.navbar-nav {
    display: flex;
    flex-direction: row;
    padding-left: 0;
    margin-bottom: 0;
    list-style: none;
}

.nav-item {
    /* margin-left: 0.5rem; */ /* 根据需要调整 */
}

.nav-link {
    display: block;
    padding: 0.5rem 1rem;
    color: var(--text-muted);
    text-decoration: none;
    border-radius: var(--border-radius-md);
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
}
.nav-link:hover {
    color: var(--text-default);
    background-color: var(--background-hover);
}
.nav-link.active {
    color: var(--text-default);
    font-weight: 600;
    /* background-color: var(--background-selected); 可选的激活背景 */
}
.nav-link .fas {
    margin-right: 0.5em;
    color: var(--text-muted); /* 图标颜色可能需要单独控制 */
}
.nav-link.active .fas {
    color: var(--color-primary); /* 激活时图标颜色 */
}
.dark-mode .nav-link.active .fas {
    color: var(--color-primary);
}


/* 暗色模式切换按钮 */
.theme-toggle {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0.5rem;
}
.theme-toggle:hover {
    color: var(--text-default);
}
```

**HTML 示例 (顶部导航)**

```html
<nav class="navbar">
    <a class="navbar-brand" href="#">NovaCloud</a>
    <ul class="navbar-nav mr-auto"> <!-- mr-auto 可以用 flex-grow-1 替代 -->
        <li class="nav-item"><a class="nav-link active" href="#"><i class="fas fa-tachometer-alt"></i> 仪表盘</a></li>
        <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-cubes"></i> 项目</a></li>
        <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-cogs"></i> 设置</a></li>
    </ul>
    <div class="user-profile d-flex align-items-center" style="margin-right: 1rem;">
        <img src="https://via.placeholder.com/32" alt="User Avatar" style="border-radius: 50%; margin-right: 0.5rem;">
        <span class="text-muted">用户名</span>
    </div>
    <button class="theme-toggle" id="themeToggleBtn">
        <i class="fas fa-moon"></i> <!-- JS会切换图标 -->
    </button>
</nav>
```

#### **3.2.2 侧边栏导航 (适用于管理面板)**

```css
/* style.css */
.sidebar {
    width: 250px;
    min-height: calc(100vh - 60px); /* 减去顶部导航栏高度 */
    background-color: var(--background-default);
    border-right: 1px solid var(--border-muted);
    padding: 1.5rem 1rem;
}
.sidebar .nav-link {
    padding: 0.75rem 1rem;
    margin-bottom: 0.25rem;
    color: var(--text-muted);
    border-left: 3px solid transparent; /* 用于激活状态指示 */
}
.sidebar .nav-link:hover {
    color: var(--text-default);
    background-color: var(--background-hover);
    border-left-color: var(--border-default);
}
.sidebar .nav-link.active {
    color: var(--text-default);
    font-weight: 600;
    background-color: var(--background-selected);
    border-left-color: var(--color-primary);
}
.sidebar .nav-link.active .fas {
    color: var(--color-primary);
}
.sidebar .menu-header {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
    color: var(--text-muted);
    padding: 1rem 1rem 0.5rem;
    margin-top: 1rem;
}
.sidebar .menu-header:first-child {
    margin-top: 0;
}
```

**HTML 示例 (侧边栏)**

```html
<div class="d-flex"> <!-- 假设外部是 flex 布局 -->
    <nav class="sidebar">
        <div class="menu-header">管理</div>
        <ul class="navbar-nav flex-column">
            <li class="nav-item"><a class="nav-link active" href="#"><i class="fas fa-users"></i> 用户管理</a></li>
            <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-shield-alt"></i> 角色权限</a></li>
        </ul>
        <div class="menu-header">物联网</div>
        <ul class="navbar-nav flex-column">
            <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-boxes"></i> 设备列表</a></li>
            <li class="nav-item"><a class="nav-link" href="#"><i class="fas fa-chart-line"></i> 数据监控</a></li>
        </ul>
    </nav>
    <main class="main-content flex-grow-1 p-4">
        <!-- 主内容区 -->
    </main>
</div>
```

### 3.3 卡片 (.card)

卡片用于组织和展示信息块。

```css
/* style.css */
.card {
    background-color: var(--background-default);
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-lg); /* GitHub 通常用 6px，但可以略大些 */
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.5rem;
    transition: box-shadow 0.2s ease-in-out;
}
.card:hover {
    /* box-shadow: var(--shadow-md); 可选的悬停阴影增强 */
}

.card-header {
    padding: 1rem 1.25rem;
    margin-bottom: 0;
    background-color: var(--background-muted); /* 略有区分的背景 */
    border-bottom: 1px solid var(--border-default);
    border-top-left-radius: calc(var(--border-radius-lg) - 1px);
    border-top-right-radius: calc(var(--border-radius-lg) - 1px);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.card-header .card-title {
    margin-bottom: 0;
    font-size: 1.15rem; /* 比 h5 稍大 */
    font-weight: 500; /* GitHub 风格标题字重通常不那么粗 */
}

.card-body {
    padding: 1.25rem;
}
.card-body > :last-child {
    margin-bottom: 0; /* 移除最后一个子元素的下边距 */
}

.card-footer {
    padding: 1rem 1.25rem;
    background-color: var(--background-muted);
    border-top: 1px solid var(--border-default);
    border-bottom-left-radius: calc(var(--border-radius-lg) - 1px);
    border-bottom-right-radius: calc(var(--border-radius-lg) - 1px);
}
```

**HTML 示例**

```html
<div class="card">
    <div class="card-header">
        <h5 class="card-title">设备概览</h5>
        <button class="btn btn-sm btn-outline-primary"><i class="fas fa-plus"></i> 添加设备</button>
    </div>
    <div class="card-body">
        <p class="text-muted">这里显示设备的关键信息和统计数据。</p>
        <p>当前在线设备：<strong class="text-success">15</strong> 台</p>
    </div>
    <div class="card-footer text-muted">
        最后更新于：3 分钟前
    </div>
</div>
```

### 3.4 状态指示器与徽章

用于显示状态、标签或计数。

```css
/* style.css */
/* 状态点 */
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 0.5em;
    vertical-align: middle; /* 确保和文本对齐 */
}
.status-dot-success { background-color: var(--color-success); }
.status-dot-danger { background-color: var(--color-danger); }
.status-dot-warning { background-color: var(--color-warning); }
.status-dot-info { background-color: var(--color-info); }
.status-dot-offline { background-color: var(--color-secondary); }


/* 徽章 */
.badge {
    display: inline-block;
    padding: 0.35em 0.65em; /* 调整内边距 */
    font-size: 0.75em;
    font-weight: 600;
    line-height: 1;
    color: #fff; /* 默认白色文字 */
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: var(--border-radius-md); /* GitHub 风格圆角较大 */
}
/* 确保暗色模式下部分徽章文字颜色反转 */
.badge-primary { background-color: var(--color-primary); color: var(--text-on-primary); }
.badge-secondary { background-color: var(--color-secondary); color: #fff; }
body.dark-mode .badge-secondary { color: var(--text-default); }
.badge-success { background-color: var(--color-success); color: #fff; }
.badge-danger { background-color: var(--color-danger); color: var(--text-on-danger); }
.badge-warning { background-color: var(--color-warning); color: #212529; } /* 黄色背景通常配深色文字 */
body.dark-mode .badge-warning { color: var(--text-default); }
.badge-info { background-color: var(--color-info); color: #fff; }
.badge-light { background-color: var(--background-muted); color: var(--text-default); }
.badge-dark { background-color: var(--text-default); color: var(--background-body); }
```

**HTML 示例**

```html
<p><span class="status-dot status-dot-success"></span>设备在线</p>
<p><span class="status-dot status-dot-offline"></span>设备离线</p>
<h4>通知 <span class="badge badge-danger">3</span></h4>
<span class="badge badge-primary">主要</span>
<span class="badge badge-warning">审核中</span>
```

### 3.5 表单元素

```css
/* style.css */
.form-group {
    margin-bottom: 1rem;
}

.form-label {
    display: inline-block;
    margin-bottom: 0.5rem;
    font-weight: 500; /* GitHub 标签字重较轻 */
    font-size: 0.875rem;
}

.form-control {
    display: block;
    width: 100%;
    padding: 0.5rem 0.75rem; /* GitHub 风格输入框padding */
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-default);
    background-color: var(--background-default);
    background-clip: padding-box;
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-md);
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.form-control:focus {
    color: var(--text-default);
    background-color: var(--background-default);
    border-color: var(--border-focus);
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(var(--color-primary-rgb), 0.25);
}
.form-control::placeholder {
    color: var(--text-placeholder);
    opacity: 1;
}
.form-control:disabled, .form-control[readonly] {
    background-color: var(--background-muted);
    opacity: 1;
}

textarea.form-control {
    min-height: calc(1.5em + 1rem + 2px); /* 调整以适应 padding 和 line-height */
    resize: vertical;
}

select.form-control {
    /* 基础样式已覆盖，可能需要为箭头做特定样式 */
}
```

**HTML 示例**

```html
<form>
    <div class="form-group">
        <label for="deviceName" class="form-label">设备名称</label>
        <input type="text" class="form-control" id="deviceName" placeholder="例如：客厅温度传感器">
    </div>
    <div class="form-group">
        <label for="deviceType" class="form-label">设备类型</label>
        <select class="form-control" id="deviceType">
            <option>传感器</option>
            <option>执行器</option>
        </select>
    </div>
    <div class="form-group">
        <label for="deviceDescription" class="form-label">描述</label>
        <textarea class="form-control" id="deviceDescription" rows="3"></textarea>
    </div>
    <button type="submit" class="btn btn-primary">提交</button>
</form>
```

### 3.6 动画与过渡

- **过渡 (Transitions)**: 主要用于交互元素的状态变化，如按钮、链接的 background-color, color, border-color, box-shadow。
    - transition-property: all; (或具体属性)
    - transition-duration: 0.15s; (快速响应)
    - transition-timing-function: ease-in-out;
- **动画 (Animations)**: 用于更复杂的视觉效果，如加载指示器、模态框的出现/消失。
    - 示例：简单的淡入动画

```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
.fade-in {
    animation: fadeIn 0.3s ease-out;
}
```

## 4. 明暗模式切换实现 (JavaScript)

script.js 文件用于处理明暗模式的切换逻辑。

```js
// js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const body = document.body;
    const moonIconClass = 'fa-moon';
    const sunIconClass = 'fa-sun';

    // Function to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            body.classList.add('dark-mode');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = `<i class="fas ${sunIconClass}"></i>`;
            }
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.remove('dark-mode');
            if (themeToggleBtn) {
                themeToggleBtn.innerHTML = `<i class="fas ${moonIconClass}"></i>`;
            }
            localStorage.setItem('theme', 'light');
        }
    }

    // Event listener for the toggle button
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            if (body.classList.contains('dark-mode')) {
                setTheme('light');
            } else {
                setTheme('dark');
            }
        });
    }

    // Apply theme on initial load
    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
        setTheme(savedTheme);
    } else if (prefersDarkScheme) {
        setTheme('dark');
    } else {
        setTheme('light'); // Default to light if no preference or saved theme
    }

    // Listen for OS theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        if (!localStorage.getItem('theme')) { // Only if user hasn't manually set a theme
            if (event.matches) {
                setTheme('dark');
            } else {
                setTheme('light');
            }
        }
    });
});
```

确保在 HTML 中引入 JS 文件：

```html
<!-- 在 </body> 闭合标签之前 -->
<script src="js/script.js"></script>
```

## 5. 文件结构总结

```
static/
├── css/
│   ├── style.css
│   └── all.min.css  (核心样式文件)
├── js/
│   └── script.js
├── fonts/
├── webfonts/
│   ├── fa-brands-400.woff2
│   ├── fa-regular-400.woff2
│   ├── fa-solid-900.woff2
│   └── ... (其他字体文件)
└── index.html (或你的 Django 模板)
```

这套 UI 样式规范提供了一个坚实的基础。在实际项目中，可以根据具体需求进一步扩展和细化组件样式，例如模态框、下拉菜单、表格、提示条等。

```css

**`style.css` 完整示例 (请将此内容保存到 `css/style.css`):**
(由于内容较长，这里仅展示关键结构，具体样式已在 Markdown 中分块给出)

```css
/* css/style.css */

/* 1. VARIABLES (ROOT & DARK MODE) */
:root {
    /* 核心色调 - 浅色模式 */
    --color-primary: #3498db;
    --color-primary-hover: #2980b9;
    --color-primary-active: #216a9a;
    --color-primary-rgb: 52, 152, 219; /* For box-shadow alpha */
    --color-secondary: #6c757d;
    --color-secondary-hover: #5a6268;
    --color-success: #28a745;
    --color-danger: #dc3545;
    --color-warning: #ffc107;
    --color-info: #17a2b8;

    /* 背景色 - 浅色模式 */
    --background-body: #f6f8fa;
    --background-default: #ffffff;
    --background-muted: #f1f3f5;
    --background-hover: #f8f9fa;
    --background-selected: #e9ecef;

    /* 文本色 - 浅色模式 */
    --text-default: #24292f;
    --text-muted: #57606a;
    --text-link: var(--color-primary);
    --text-placeholder: #8b949e;
    --text-on-primary: #ffffff;
    --text-on-danger: #ffffff;

    /* 边框色 - 浅色模式 */
    --border-default: #d0d7de;
    --border-muted: #e1e4e8;
    --border-focus: var(--color-primary);

    /* 阴影 */
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.075);
    --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.1);

    /* 其他 */
    --border-radius-sm: 0.25rem; /* 4px */
    --border-radius-md: 0.375rem; /* 6px */
    --border-radius-lg: 0.5rem;  /* 8px */

    --font-family-sans-serif: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
    --font-family-monospace: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
}

body.dark-mode {
    --color-primary: #58a6ff;
    --color-primary-hover: #79b8ff;
    --color-primary-active: #4191e1;
    --color-primary-rgb: 88, 166, 255;
    --color-secondary: #8b949e;
    --color-secondary-hover: #a0aec0;
    --color-success: #3fb950;
    --color-danger: #f85149;
    --color-warning: #e3b341;
    --color-info: #58a6ff;

    --background-body: #0d1117;
    --background-default: #161b22;
    --background-muted: #010409;
    --background-hover: #222831;
    --background-selected: #2a3038;

    --text-default: #e6edf3;
    --text-muted: #7d8590;
    --text-link: var(--color-primary);
    --text-placeholder: #6e7681;
    --text-on-primary: #0d1117;
    --text-on-danger: #ffffff;

    --border-default: #30363d;
    --border-muted: #21262d;
    --border-focus: var(--color-primary);

    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.15);
    --shadow-md: 0 3px 6px rgba(0, 0, 0, 0.2);
    --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* 2. BASE STYLES (BODY, TYPOGRAPHY, LINKS) */
body {
    font-family: var(--font-family-sans-serif);
    font-size: 1rem;
    line-height: 1.6;
    color: var(--text-default);
    background-color: var(--background-body);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    margin: 0;
    transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out; /* Smooth theme transition */
}

h1, .h1 { font-size: 2rem; line-height: 1.2; margin-top:0; margin-bottom: 0.75rem; font-weight: 600; }
h2, .h2 { font-size: 1.75rem; line-height: 1.25; margin-top:0; margin-bottom: 0.6rem; font-weight: 600; }
h3, .h3 { font-size: 1.5rem; line-height: 1.3; margin-top:0; margin-bottom: 0.5rem; font-weight: 600; }
h4, .h4 { font-size: 1.25rem; line-height: 1.35; margin-top:0; margin-bottom: 0.4rem; font-weight: 600; }
h5, .h5 { font-size: 1.1rem; line-height: 1.4; margin-top:0; margin-bottom: 0.3rem; font-weight: 600; }
h6, .h6 { font-size: 1rem; line-height: 1.4; margin-top:0; margin-bottom: 0.25rem; font-weight: 600; }

p { margin-top:0; margin-bottom: 1rem; }
a { color: var(--text-link); text-decoration: none; transition: color 0.15s ease-in-out; }
a:hover { color: var(--color-primary-hover); text-decoration: underline; }

small, .text-small { font-size: 0.875em; }
.text-muted { color: var(--text-muted) !important; }
strong, b { font-weight: 600; }

/* 3. LAYOUT (CONTAINER, FLEX UTILS) */
.container {
    width: 100%;
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
    box-sizing: border-box;
}
@media (min-width: 576px) { .container { max-width: 540px; } }
@media (min-width: 768px) { .container { max-width: 720px; } }
@media (min-width: 992px) { .container { max-width: 960px; } }
@media (min-width: 1200px) { .container { max-width: 1140px; } }

.d-flex { display: flex !important; }
.align-items-center { align-items: center !important; }
.justify-content-between { justify-content: space-between !important; }
.justify-content-center { justify-content: center !important; }
.flex-grow-1 { flex-grow: 1 !important; }
.flex-column { flex-direction: column !important; }
.mr-auto { margin-right: auto !important; } /* For pushing items in flex */
.ml-auto { margin-left: auto !important; }
.p-4 { padding: 1.5rem !important; } /* Example padding utility */


/* 4. COMPONENTS */

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    line-height: 1.5;
    color: var(--text-default);
    text-align: center;
    vertical-align: middle;
    cursor: pointer;
    user-select: none;
    background-color: var(--background-default);
    border: 1px solid var(--border-default);
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    border-radius: var(--border-radius-md);
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.btn:hover {
    border-color: var(--border-muted);
    /* For non-primary buttons, slight background change on hover */
}
.btn:not(.btn-primary):not(.btn-danger):not(.btn-outline-primary):hover {
    background-color: var(--background-hover);
}
.btn:focus, .btn.focus {
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(var(--color-primary-rgb), 0.25);
}
.btn:active, .btn.active {
    /* Subtle active state */
}
.btn.disabled, .btn:disabled {
    opacity: 0.65;
    pointer-events: none;
}
.btn-primary {
    color: var(--text-on-primary);
    background-color: var(--color-primary);
    border-color: var(--color-primary);
}
.btn-primary:hover {
    color: var(--text-on-primary);
    background-color: var(--color-primary-hover);
    border-color: var(--color-primary-hover);
}
.btn-primary:active {
    color: var(--text-on-primary);
    background-color: var(--color-primary-active);
    border-color: var(--color-primary-active);
}
.btn-secondary {
    color: var(--text-default);
    background-color: var(--background-muted);
    border-color: var(--border-default);
}
body.dark-mode .btn-secondary {
    color: var(--text-default);
}
.btn-secondary:hover {
    background-color: var(--background-selected);
    border-color: var(--border-muted);
}
.btn-outline-primary {
    color: var(--color-primary);
    border-color: var(--color-primary);
    background-color: transparent;
}
.btn-outline-primary:hover {
    color: var(--text-on-primary);
    background-color: var(--color-primary);
    border-color: var(--color-primary);
}
.btn-danger {
    color: var(--text-on-danger);
    background-color: var(--color-danger);
    border-color: var(--color-danger);
}
body:not(.dark-mode) .btn-danger:hover { background-color: #c82333; border-color: #bd2130; }
body.dark-mode .btn-danger:hover { background-color: #eA433c; border-color: #e0312a; }

.btn-sm {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
    border-radius: var(--border-radius-sm);
}
.btn-lg {
    padding: 0.65rem 1.25rem;
    font-size: 1rem;
    border-radius: var(--border-radius-md);
}
.btn .fas, .btn .far, .btn .fab {
    margin-right: 0.5em;
    font-size: 0.9em;
}
.btn .fas:only-child, .btn .far:only-child, .btn .fab:only-child {
    margin-right: 0;
}


/* Navbar */
.navbar {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    background-color: var(--background-default);
    border-bottom: 1px solid var(--border-muted);
    box-shadow: var(--shadow-sm);
    min-height: 60px; /* Ensure consistent height */
    box-sizing: border-box;
}
.navbar-brand {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--text-default);
    margin-right: 1.5rem;
    text-decoration: none;
}
.navbar-brand:hover {
    color: var(--text-default);
    text-decoration: none;
}
.navbar-nav {
    display: flex;
    flex-direction: row;
    padding-left: 0;
    margin-bottom: 0;
    list-style: none;
}
.nav-item {
    /* margin-left: 0.5rem; */
}
.nav-link {
    display: block;
    padding: 0.5rem 1rem;
    color: var(--text-muted);
    text-decoration: none;
    border-radius: var(--border-radius-md);
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
}
.nav-link:hover {
    color: var(--text-default);
    background-color: var(--background-hover);
}
.nav-link.active {
    color: var(--text-default);
    font-weight: 600;
}
.nav-link .fas, .nav-link .far, .nav-link .fab {
    margin-right: 0.5em;
    color: var(--text-muted); /* Default icon color in nav links */
}
.nav-link:hover .fas, .nav-link:hover .far, .nav-link:hover .fab {
    color: var(--text-default); /* Icon color on nav link hover */
}
.nav-link.active .fas, .nav-link.active .far, .nav-link.active .fab {
    color: var(--color-primary); /* Active nav link icon color */
}

.theme-toggle {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0.5rem;
    margin-left: auto; /* Push to the right */
}
.theme-toggle:hover {
    color: var(--text-default);
}


/* Sidebar */
.sidebar {
    width: 250px;
    min-height: calc(100vh - 60px); /* Assuming 60px navbar height */
    background-color: var(--background-default);
    border-right: 1px solid var(--border-muted);
    padding: 1.5rem 1rem;
    box-sizing: border-box;
    flex-shrink: 0; /* Prevent shrinking in flex container */
}
.sidebar .navbar-nav { /* For vertical nav in sidebar */
    flex-direction: column;
}
.sidebar .nav-link {
    padding: 0.75rem 1rem;
    margin-bottom: 0.25rem;
    color: var(--text-muted);
    border-left: 3px solid transparent;
}
.sidebar .nav-link:hover {
    color: var(--text-default);
    background-color: var(--background-hover);
    border-left-color: var(--border-default);
}
.sidebar .nav-link.active {
    color: var(--text-default);
    font-weight: 600;
    background-color: var(--background-selected);
    border-left-color: var(--color-primary);
}
.sidebar .nav-link.active .fas,
.sidebar .nav-link.active .far,
.sidebar .nav-link.active .fab {
    color: var(--color-primary);
}
.sidebar .menu-header {
    font-size: 0.75rem;
    text-transform: uppercase;
    font-weight: 600;
    color: var(--text-muted);
    padding: 1rem 1rem 0.5rem;
    margin-top: 1rem;
}
.sidebar .menu-header:first-child {
    margin-top: 0;
}

.main-content { /* Example class for main content area next to sidebar */
    padding: 1.5rem;
    box-sizing: border-box;
    flex-grow: 1;
}


/* Cards */
.card {
    background-color: var(--background-default);
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-sm);
    margin-bottom: 1.5rem;
    transition: box-shadow 0.2s ease-in-out;
}
.card-header {
    padding: 1rem 1.25rem;
    margin-bottom: 0;
    background-color: var(--background-muted);
    border-bottom: 1px solid var(--border-default);
    border-top-left-radius: calc(var(--border-radius-lg) - 1px); /* Adjust for border */
    border-top-right-radius: calc(var(--border-radius-lg) - 1px);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.card-header .card-title {
    margin-bottom: 0;
    font-size: 1.15rem;
    font-weight: 500;
}
.card-body {
    padding: 1.25rem;
}
.card-body > :last-child {
    margin-bottom: 0;
}
.card-footer {
    padding: 1rem 1.25rem;
    background-color: var(--background-muted);
    border-top: 1px solid var(--border-default);
    border-bottom-left-radius: calc(var(--border-radius-lg) - 1px);
    border-bottom-right-radius: calc(var(--border-radius-lg) - 1px);
}


/* Status & Badges */
.status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 0.5em;
    vertical-align: middle;
}
.status-dot-success { background-color: var(--color-success); }
.status-dot-danger { background-color: var(--color-danger); }
.status-dot-warning { background-color: var(--color-warning); }
.status-dot-info { background-color: var(--color-info); }
.status-dot-offline { background-color: var(--color-secondary); }

.badge {
    display: inline-block;
    padding: 0.35em 0.65em;
    font-size: 0.75em;
    font-weight: 600;
    line-height: 1;
    color: #fff;
    text-align: center;
    white-space: nowrap;
    vertical-align: baseline;
    border-radius: var(--border-radius-md);
}
.badge-primary { background-color: var(--color-primary); color: var(--text-on-primary); }
.badge-secondary { background-color: var(--color-secondary); color: #fff; }
body.dark-mode .badge-secondary { color: var(--text-default); }
.badge-success { background-color: var(--color-success); color: #fff; }
.badge-danger { background-color: var(--color-danger); color: var(--text-on-danger); }
.badge-warning { background-color: var(--color-warning); color: #212529; }
body.dark-mode .badge-warning { color: var(--text-default); }
.badge-info { background-color: var(--color-info); color: #fff; }
.badge-light { background-color: var(--background-muted); color: var(--text-default); }
.badge-dark { background-color: var(--text-default); color: var(--background-body); }


/* Forms */
.form-group {
    margin-bottom: 1rem;
}
.form-label {
    display: inline-block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    font-size: 0.875rem;
}
.form-control {
    display: block;
    width: 100%;
    box-sizing: border-box; /* Ensure padding and border don't add to width */
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
    color: var(--text-default);
    background-color: var(--background-default);
    background-clip: padding-box;
    border: 1px solid var(--border-default);
    border-radius: var(--border-radius-md);
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}
.form-control:focus {
    color: var(--text-default);
    background-color: var(--background-default);
    border-color: var(--border-focus);
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(var(--color-primary-rgb), 0.25);
}
.form-control::placeholder {
    color: var(--text-placeholder);
    opacity: 1;
}
.form-control:disabled, .form-control[readonly] {
    background-color: var(--background-muted);
    opacity: 1;
}
textarea.form-control {
    min-height: calc(1.5em * 3 + 1rem + 2px); /* Approx 3 lines */
    resize: vertical;
}


/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
.fade-in {
    animation: fadeIn 0.3s ease-out;
}

/* Example for a spinner/loader - can be expanded */
.spinner {
    display: inline-block;
    width: 1.5rem;
    height: 1.5rem;
    vertical-align: text-bottom;
    border: 0.2em solid currentColor;
    border-right-color: transparent;
    border-radius: 50%;
    animation: spinner-border .75s linear infinite;
    color: var(--color-primary); /* Default spinner color */
}
@keyframes spinner-border {
    to { transform: rotate(360deg); }
}
.spinner-sm {
    width: 1rem;
    height: 1rem;
    border-width: 0.15em;
}

/* User Profile snippet in Navbar */
.user-profile img {
    border-radius: 50%;
    margin-right: 0.5rem;
    width: 32px;
    height: 32px;
}
```

**cript.js (内容已在 Markdown 中提供，请保存到 js/script.js)**

**本地化 Font Awesome:**

1. 访问 [Font Awesome 官网](https://www.google.com/url?sa=E&q=https%3A%2F%2Ffontawesome.com%2Fdownload)。
2. 下载 "Free For Web" 版本。
3. 解压下载的 fontawesome-free-X.X.X-web.zip 文件。
4. 将解压后的 css 文件夹中的 all.min.css 文件复制到你的项目 fonts/fontawesome/css/ 目录下。
5. 将解压后的 webfonts 文件夹整个复制到你的项目 fonts/fontawesome/ 目录下。
    最终目录结构应如 Markdown 文档中所示。

这套设计和文件为你提供了一个良好的开端。你可以根据 NovaCloud 项目的具体需求继续添加和完善更多组件。



