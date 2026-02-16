/**
 * Flask 博客系统 - 前端交互脚本
 * 包含各种交互功能的实现
 */

// ==================== 页面加载完成后执行 ====================

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initAutoHideAlerts();
    initSmoothScroll();
    initFormValidation();
});

// ==================== 自动隐藏提示消息 ====================

/**
 * 自动隐藏 Flash 消息
 * 5秒后自动关闭提示框
 */
function initAutoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        // 5秒后自动关闭
        setTimeout(function() {
            // 使用 Bootstrap 的关闭方法
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// ==================== 平滑滚动 ====================

/**
 * 初始化平滑滚动
 * 点击锚点链接时平滑滚动到目标位置
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ==================== 表单验证 ====================

/**
 * 初始化表单验证增强
 * 为表单添加客户端验证
 */
function initFormValidation() {
    // 获取所有需要验证的表单
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// ==================== 评论功能 ====================

/**
 * 预览评论
 * 在提交前预览评论内容
 * @param {string} author - 评论者名称
 * @param {string} content - 评论内容
 */
function previewComment(author, content) {
    const previewHtml = `
        <div class="card">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">评论预览</h6>
                <p class="card-text"><strong>${escapeHtml(author)}:</strong> ${escapeHtml(content)}</p>
            </div>
        </div>
    `;

    // 查找或创建预览容器
    let previewContainer = document.getElementById('comment-preview');
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = 'comment-preview';
        previewContainer.className = 'mt-3';

        const form = document.querySelector('form[action*="comment"]');
        if (form) {
            form.parentNode.insertBefore(previewContainer, form.nextSibling);
        }
    }

    previewContainer.innerHTML = previewHtml;
}

// ==================== 搜索功能 ====================

/**
 * 搜索关键词高亮
 * 在搜索结果中高亮显示关键词
 * @param {string} keyword - 要高亮的关键词
 */
function highlightSearchKeyword(keyword) {
    if (!keyword) return;

    const contentElements = document.querySelectorAll('.card-text');
    const regex = new RegExp(`(${escapeRegExp(keyword)})`, 'gi');

    contentElements.forEach(element => {
        element.innerHTML = element.innerHTML.replace(
            regex,
            '<mark class="bg-warning">$1</mark>'
        );
    });
}

// ==================== 工具函数 ====================

/**
 * HTML 转义
 * 防止 XSS 攻击
 * @param {string} text - 原始文本
 * @returns {string} - 转义后的文本
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 正则表达式转义
 * @param {string} string - 原始字符串
 * @returns {string} - 转义后的字符串
 */
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * 复制到剪贴板
 * @param {string} text - 要复制的文本
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('已复制到剪贴板', 'success');
    }, function(err) {
        console.error('复制失败:', err);
        showToast('复制失败', 'error');
    });
}

/**
 * 显示 Toast 提示
 * @param {string} message - 消息内容
 * @param {string} type - 类型 (success, error, warning, info)
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();

    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    toast.show();

    // 自动移除 DOM
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

/**
 * 创建 Toast 容器
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// ==================== 返回顶部按钮 ====================

/**
 * 初始化返回顶部按钮
 */
function initBackToTop() {
    // 创建按钮
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'back-to-top';
    backToTopBtn.className = 'btn btn-primary btn-sm position-fixed';
    backToTopBtn.style.cssText = 'bottom: 20px; right: 20px; display: none; z-index: 1000;';
    backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopBtn.setAttribute('aria-label', '返回顶部');

    document.body.appendChild(backToTopBtn);

    // 滚动时显示/隐藏按钮
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });

    // 点击返回顶部
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 页面加载时初始化返回顶部按钮
if (document.body) {
    initBackToTop();
} else {
    document.addEventListener('DOMContentLoaded', initBackToTop);
}

// ==================== 图片懒加载 ====================

/**
 * 初始化图片懒加载
 */
function initLazyLoad() {
    const images = document.querySelectorAll('img[data-src]');

    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    } else {
        // 浏览器不支持 IntersectionObserver 时直接加载
        images.forEach(img => {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
        });
    }
}

// 页面加载完成后初始化懒加载
document.addEventListener('DOMContentLoaded', initLazyLoad);
