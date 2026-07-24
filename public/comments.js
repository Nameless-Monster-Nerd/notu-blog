// Comments system for Studio Skills guides
// Uses Cloudflare Worker API for storage

const COMMENTS_API = 'https://comment-worker.nasirullah-mohammad.workers.dev';

async function loadComments(page) {
  try {
    const res = await fetch(`${COMMENTS_API}/comments?page=${encodeURIComponent(page)}`);
    const data = await res.json();
    return data.comments || [];
  } catch (e) {
    console.error('Failed to load comments:', e);
    return [];
  }
}

async function submitComment(event, page) {
  event.preventDefault();
  
  const form = event.target;
  const nameInput = form.querySelector('#comment-name');
  const textInput = form.querySelector('#comment-text');
  const status = form.querySelector('#comment-status');
  
  const name = nameInput.value.trim();
  const text = textInput.value.trim();
  
  if (!name || !text) {
    status.textContent = 'Please fill in both fields.';
    status.style.color = '#ff7a30';
    return false;
  }
  
  status.textContent = 'Posting...';
  status.style.color = '#888';
  
  try {
    const res = await fetch(`${COMMENTS_API}/comment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page, name, text })
    });
    
    const data = await res.json();
    
    if (data.success) {
      nameInput.value = '';
      textInput.value = '';
      status.textContent = '✅ Comment posted!';
      status.style.color = '#4ade80';
      // Reload comments
      renderComments(page);
    } else {
      status.textContent = '❌ Failed to post. Try again.';
      status.style.color = '#ff7a30';
    }
  } catch (e) {
    status.textContent = '❌ Network error. Check your connection.';
    status.style.color = '#ff7a30';
  }
  
  return false;
}

async function renderComments(page) {
  const list = document.getElementById('comments-list');
  if (!list) return;
  
  const comments = await loadComments(page);
  
  if (comments.length === 0) {
    list.innerHTML = '<p style="color:#888;font-style:italic;">No comments yet. Be the first to share!</p>';
    return;
  }
  
  list.innerHTML = comments.map(c => `
    <div class="comment-item">
      <div class="comment-header">
        <strong>${escapeHtml(c.name)}</strong>
        <span class="comment-date">${new Date(c.timestamp).toLocaleDateString()}</span>
      </div>
      <div class="comment-body">${escapeHtml(c.text)}</div>
      ${c.replies && c.replies.length > 0 ? `
        <div class="comment-replies">
          ${c.replies.map(r => `
            <div class="reply-item">
              <strong>${escapeHtml(r.name)}</strong>
              <span class="comment-date">${new Date(r.timestamp).toLocaleDateString()}</span>
              <p>${escapeHtml(r.text)}</p>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `).join('');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Auto-load comments on page load
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('comment-form');
  if (form) {
    const page = form.getAttribute('onsubmit')?.match(/'([^']+)'/)?.[1];
    if (page) renderComments(page);
  }
});
