/**
 * 秋招卡片编辑功能
 */

/**
 * 进入编辑模式
 * @param {number} docId 文档ID
 */
function editCard(docId) {
    const card = document.querySelector(`[data-doc-id="${docId}"]`);
    if (!card) return;
    
    const displayMode = card.querySelector('.card__display-mode');
    const editMode = card.querySelector('.card__edit-mode');
    
    if (displayMode && editMode) {
        displayMode.style.display = 'none';
        editMode.style.display = 'block';
        
        // 自动调整 textarea 高度
        const textarea = editMode.querySelector('textarea');
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = textarea.scrollHeight + 'px';
        }
    }
}

/**
 * 取消编辑模式
 * @param {number} docId 文档ID
 */
function cancelEdit(docId) {
    const card = document.querySelector(`[data-doc-id="${docId}"]`);
    if (!card) return;
    
    const displayMode = card.querySelector('.card__display-mode');
    const editMode = card.querySelector('.card__edit-mode');
    
    if (displayMode && editMode) {
        displayMode.style.display = 'block';
        editMode.style.display = 'none';
    }
}
