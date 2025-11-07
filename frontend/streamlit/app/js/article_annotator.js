/**
 * Article Annotator - 文章批注工具
 * 
 * 功能：
 * 1. 支持文本选择和高亮
 * 2. 添加批注和评论
 * 3. 管理批注数据
 * 4. 与 Streamlit 通信
 * 
 * @version 1.0.0
 * @author Auto-doc-streamlit
 */

class ArticleAnnotator {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with id "${containerId}" not found`);
        }

        // 配置选项
        this.options = {
            highlightColor: options.highlightColor || '#fff59d',
            selectedColor: options.selectedColor || '#ffeb3b',
            readOnly: options.readOnly || false,
            ...options
        };

        // 批注数据存储
        this.annotations = [];
        this.selectedAnnotationId = null;

        // 初始化
        this.init();
    }

    /**
     * 初始化批注工具
     */
    init() {
        if (this.options.readOnly) {
            // 只读模式，只渲染已有批注
            this.renderAnnotations();
            return;
        }

        // 编辑模式，添加事件监听
        this.container.addEventListener('mouseup', this.handleTextSelection.bind(this));
        
        // 创建批注工具栏
        this.createToolbar();
        
        // 渲染已有批注
        this.renderAnnotations();
    }

    /**
     * 处理文本选择
     */
    handleTextSelection(event) {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText.length === 0) {
            this.hideToolbar();
            return;
        }

        // 获取选择的范围
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // 显示工具栏
        this.showToolbar(rect, selectedText, range);
    }

    /**
     * 创建工具栏
     */
    createToolbar() {
        this.toolbar = document.createElement('div');
        this.toolbar.id = 'annotation-toolbar';
        this.toolbar.style.cssText = `
            position: fixed;
            display: none;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            padding: 12px;
            z-index: 10000;
            min-width: 320px;
        `;

        this.toolbar.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong style="color: #2B2B2B; font-size: 14px;">添加批注</strong>
            </div>
            <div style="margin-bottom: 10px;">
                <select id="annotation-type" style="
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 13px;
                ">
                    <option value="language">📝 语言问题</option>
                    <option value="fact">📊 事实错误</option>
                    <option value="content">💡 内容建议</option>
                    <option value="style">⚠️ 风格问题</option>
                    <option value="format">🔧 格式问题</option>
                </select>
            </div>
            <div style="margin-bottom: 10px;">
                <select id="annotation-severity" style="
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 13px;
                ">
                    <option value="low">低 - 可选修改</option>
                    <option value="medium" selected>中 - 建议修改</option>
                    <option value="high">高 - 必须修改</option>
                </select>
            </div>
            <div style="margin-bottom: 10px;">
                <textarea id="annotation-content" placeholder="批注内容..." style="
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 13px;
                    min-height: 60px;
                    resize: vertical;
                "></textarea>
            </div>
            <div style="display: flex; gap: 8px;">
                <button id="save-annotation" style="
                    flex: 1;
                    padding: 8px 16px;
                    background: #E8957B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    font-weight: 500;
                ">保存</button>
                <button id="cancel-annotation" style="
                    flex: 1;
                    padding: 8px 16px;
                    background: #ddd;
                    color: #666;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                ">取消</button>
            </div>
        `;

        document.body.appendChild(this.toolbar);

        // 绑定按钮事件
        document.getElementById('save-annotation').addEventListener('click', () => {
            this.saveAnnotation();
        });

        document.getElementById('cancel-annotation').addEventListener('click', () => {
            this.hideToolbar();
        });
    }

    /**
     * 显示工具栏
     */
    showToolbar(rect, selectedText, range) {
        this.toolbar.style.display = 'block';
        this.toolbar.style.left = `${rect.left}px`;
        this.toolbar.style.top = `${rect.bottom + 10}px`;

        // 存储当前选择信息
        this.currentSelection = {
            text: selectedText,
            range: range,
            rect: rect
        };

        // 清空上次的内容
        document.getElementById('annotation-content').value = '';
    }

    /**
     * 隐藏工具栏
     */
    hideToolbar() {
        this.toolbar.style.display = 'none';
        this.currentSelection = null;
        window.getSelection().removeAllRanges();
    }

    /**
     * 保存批注
     */
    saveAnnotation() {
        if (!this.currentSelection) return;

        const type = document.getElementById('annotation-type').value;
        const severity = document.getElementById('annotation-severity').value;
        const content = document.getElementById('annotation-content').value.trim();

        if (!content) {
            alert('请输入批注内容');
            return;
        }

        // 创建批注对象
        const annotation = {
            id: this.generateId(),
            quote: this.currentSelection.text,
            type: type,
            severity: severity,
            content: content,
            created_at: new Date().toISOString(),
            // 保存位置信息（用于重新定位）
            position: {
                startOffset: this.currentSelection.range.startOffset,
                endOffset: this.currentSelection.range.endOffset,
                startContainer: this.getNodePath(this.currentSelection.range.startContainer),
                endContainer: this.getNodePath(this.currentSelection.range.endContainer)
            }
        };

        // 添加到批注列表
        this.annotations.push(annotation);

        // 高亮选中的文本
        this.highlightAnnotation(annotation);

        // 通知 Streamlit（如果在 Streamlit 环境中）
        this.notifyStreamlit({
            type: 'annotation_added',
            annotation: annotation,
            all_annotations: this.annotations
        });

        // 隐藏工具栏
        this.hideToolbar();
    }

    /**
     * 高亮批注文本
     */
    highlightAnnotation(annotation) {
        const span = document.createElement('span');
        span.className = 'annotation-highlight';
        span.dataset.annotationId = annotation.id;
        span.style.cssText = `
            background-color: ${this.options.highlightColor};
            cursor: pointer;
            border-bottom: 2px solid ${this.getSeverityColor(annotation.severity)};
            padding: 2px 0;
            position: relative;
        `;

        // 添加点击事件
        span.addEventListener('click', (e) => {
            e.stopPropagation();
            this.showAnnotationDetails(annotation.id);
        });

        // 包裹选中的文本
        try {
            this.currentSelection.range.surroundContents(span);
        } catch (e) {
            console.error('无法高亮文本，可能跨越了多个节点', e);
        }
    }

    /**
     * 根据严重程度获取颜色
     */
    getSeverityColor(severity) {
        const colors = {
            low: '#4caf50',
            medium: '#ff9800',
            high: '#f44336'
        };
        return colors[severity] || colors.medium;
    }

    /**
     * 显示批注详情
     */
    showAnnotationDetails(annotationId) {
        const annotation = this.annotations.find(a => a.id === annotationId);
        if (!annotation) return;

        // 高亮选中的批注
        document.querySelectorAll('.annotation-highlight').forEach(el => {
            el.style.backgroundColor = this.options.highlightColor;
        });
        const element = document.querySelector(`[data-annotation-id="${annotationId}"]`);
        if (element) {
            element.style.backgroundColor = this.options.selectedColor;
        }

        // 通知 Streamlit 显示详情
        this.notifyStreamlit({
            type: 'annotation_selected',
            annotation: annotation
        });

        this.selectedAnnotationId = annotationId;
    }

    /**
     * 删除批注
     */
    deleteAnnotation(annotationId) {
        // 从数组中移除
        this.annotations = this.annotations.filter(a => a.id !== annotationId);

        // 移除高亮
        const element = document.querySelector(`[data-annotation-id="${annotationId}"]`);
        if (element) {
            const parent = element.parentNode;
            while (element.firstChild) {
                parent.insertBefore(element.firstChild, element);
            }
            parent.removeChild(element);
        }

        // 通知 Streamlit
        this.notifyStreamlit({
            type: 'annotation_deleted',
            annotation_id: annotationId,
            all_annotations: this.annotations
        });
    }

    /**
     * 渲染已有批注
     */
    renderAnnotations() {
        // 根据保存的位置信息重新高亮文本
        this.annotations.forEach(annotation => {
            // 这里需要根据 position 信息重新创建 range
            // 简化实现：只在编辑模式下处理新批注
            // 已有批注的渲染需要更复杂的逻辑
        });
    }

    /**
     * 加载批注数据
     */
    loadAnnotations(annotations) {
        this.annotations = annotations || [];
        this.renderAnnotations();
    }

    /**
     * 获取所有批注
     */
    getAnnotations() {
        return this.annotations;
    }

    /**
     * 生成唯一ID
     */
    generateId() {
        return 'anno_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    /**
     * 获取节点路径（用于定位）
     */
    getNodePath(node) {
        const path = [];
        while (node && node !== this.container) {
            const parent = node.parentNode;
            const index = Array.from(parent.childNodes).indexOf(node);
            path.unshift(index);
            node = parent;
        }
        return path;
    }

    /**
     * 通知 Streamlit
     */
    notifyStreamlit(data) {
        if (window.parent) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: data
            }, '*');
        }
    }

    /**
     * 导出批注数据（JSON格式）
     */
    exportAnnotations() {
        return JSON.stringify(this.annotations, null, 2);
    }

    /**
     * 销毁批注工具
     */
    destroy() {
        if (this.toolbar) {
            this.toolbar.remove();
        }
        
        // 移除所有高亮
        document.querySelectorAll('.annotation-highlight').forEach(el => {
            const parent = el.parentNode;
            while (el.firstChild) {
                parent.insertBefore(el.firstChild, el);
            }
            parent.removeChild(el);
        });
    }
}

// 导出到全局作用域
window.ArticleAnnotator = ArticleAnnotator;

