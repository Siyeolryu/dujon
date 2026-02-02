/**
 * 공통 UI: 토스트, 로딩, 모달, 뱃지
 */
const UI = {
    toastTimeout: null,

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        if (this.toastTimeout) clearTimeout(this.toastTimeout);
        const colors = { success: '#27ae60', error: '#e74c3c', warning: '#f39c12', info: '#3498db' };
        const bg = colors[type] || colors.info;
        const el = document.createElement('div');
        el.className = 'toast toast-' + type;
        el.style.background = bg;
        el.textContent = message;
        container.innerHTML = '';
        container.appendChild(el);
        container.classList.add('visible');
        this.toastTimeout = setTimeout(() => {
            container.classList.remove('visible');
        }, 3000);
    },

    showLoading(target = 'body') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    },

    hideLoading(target = 'body') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    },

    async confirm(title, message) {
        return new Promise((resolve) => {
            const overlay = document.getElementById('modalOverlay');
            const titleEl = document.getElementById('modalTitle');
            const bodyEl = document.getElementById('modalBody');
            const cancelBtn = document.getElementById('modalCancel');
            const confirmBtn = document.getElementById('modalConfirm');
            if (!overlay || !titleEl || !bodyEl || !cancelBtn || !confirmBtn) {
                resolve(confirm(message));
                return;
            }
            titleEl.textContent = title;
            bodyEl.textContent = message;
            overlay.classList.remove('hidden');
            const done = (ok) => {
                overlay.classList.add('hidden');
                cancelBtn.removeEventListener('click', onCancel);
                confirmBtn.removeEventListener('click', onConfirm);
                resolve(ok);
            };
            const onCancel = () => done(false);
            const onConfirm = () => done(true);
            cancelBtn.addEventListener('click', onCancel);
            confirmBtn.addEventListener('click', onConfirm);
        });
    },

    showModal(title, contentHTML) {
        const overlay = document.getElementById('modalOverlay');
        const titleEl = document.getElementById('modalTitle');
        const bodyEl = document.getElementById('modalBody');
        const cancelBtn = document.getElementById('modalCancel');
        const confirmBtn = document.getElementById('modalConfirm');
        if (!overlay || !titleEl || !bodyEl) return;
        titleEl.textContent = title;
        bodyEl.innerHTML = contentHTML;
        overlay.classList.remove('hidden');
        if (cancelBtn) cancelBtn.style.display = 'inline-block';
        if (confirmBtn) confirmBtn.style.display = 'inline-block';
    },

    closeModal() {
        const overlay = document.getElementById('modalOverlay');
        if (overlay) overlay.classList.add('hidden');
    },

    createBadge(text, colorMap) {
        const color = (colorMap && colorMap[text]) || '#95a5a6';
        const span = document.createElement('span');
        span.className = 'badge';
        span.style.background = color;
        span.textContent = text;
        return span;
    },
};
