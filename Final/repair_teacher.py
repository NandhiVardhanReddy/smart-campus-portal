
import os

file_path = r'c:/Users/varsh/Desktop/Final/teacher.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Define the code blocks to insert

missing_functions_1 = """
            container.scrollIntoView({ behavior: 'smooth' });
            if (highlightId) {
                setTimeout(() => {
                    const el = document.getElementById('card_' + highlightId);
                    if (el) {
                        el.style.boxShadow = '0 18px 46px rgba(124,58,237,0.12)';
                        setTimeout(() => el.style.boxShadow = '0 8px 24px rgba(9,30,66,0.04)', 1800);
                    }
                }, 100);
            }
        }

        function setView(v) {
            state.view = v;
            renderLibrary(state.currentLibraryPage);
        }

        function clearLibraryFilters() {
            const subj = document.getElementById('filterSubject');
            const type = document.getElementById('filterType');
            const sort = document.getElementById('sortSelect');
            
            if(subj) subj.value = '';
            if(type) type.value = '';
            if(sort) sort.value = 'likes';
            
            renderLibrary(1);
        }

        function selectDoc(id) {
            let doc = state.docs.find(d => d.id === id);
            if (!doc && state.results.length > 0) {
                const res = state.results.find(r => r.document && r.document.id === id);
                if (res) doc = res.document;
            }
            state.selected = doc || null;
        }

        function openReview(id) {
            openReviewModal(id);
        }

        function openReviewModal(id) {
            const doc = state.docs.find(d => d.id === id);
            if (!doc) return;

            openModal('Write Review', `
    <div style="text-align:center">
      <div style="font-weight:700;margin-bottom:8px">${escapeHtml(doc.title)}</div>
      <div style="margin-bottom:16px">Rate this material:</div>
      <div style="display:flex;justify-content:center;gap:8px;margin-bottom:16px">
        ${[1, 2, 3, 4, 5].map(i => `
          <button class="star-btn" onclick="setRating(${i})" data-rating="${i}" style="background:none;border:none;font-size:24px;cursor:pointer;color:${i <= 3 ? '#f59e0b' : '#d1d5db'}">★</button>
        `).join('')}
      </div>
      <textarea id="reviewText" placeholder="Write your review here..." style="width:100%;height:100px;padding:10px;border-radius:8px;border:1px solid rgba(15,23,42,0.1);margin-bottom:16px"></textarea>
      <button class="btn-primary" onclick="submitReview('${doc.id}')">Submit Review</button>
    </div>
  `);
        }

        function setRating(r) {
            const stars = document.querySelectorAll('.star-btn');
            stars.forEach(s => {
                const val = parseInt(s.dataset.rating);
                s.style.color = val <= r ? '#f59e0b' : '#d1d5db';
            });
        }

"""

missing_functions_2 = """
            function fallbackSearch(query) {
                const hits = state.docs.filter(d => {
                    const hay = `${d.title} ${d.content || ''} ${d.filename} ${d.subject || ''}`.toLowerCase();
                    return query.toLowerCase().split(/\s+/).every(tok => hay.includes(tok));
                }).map(doc => ({
                    document: doc,
                    score: Math.random() * 0.5 + 0.5,
                    highlights: [
                        `Found match for "${query}" in ${doc.title}`,
                        doc.content.substring(0, 150) + '...'
                    ],
                    search_type: 'keyword'
                }));

                state.isSearching = true;
                state.currentQuery = query;
                state.results = hits;
                renderLibrary(1);
            }

        function clearSearch() {
            state.isSearching = false;
            state.currentQuery = '';
            state.results = [];
            const topSearch = document.getElementById('topSearch');
            if(topSearch) topSearch.value = '';
            renderLibrary(1);
        }

        function selectAndOpen(id) {
            selectDoc(id);
            openPreviewModalById(id);
        }

        /* PREVIEW MODAL */
        async function openPreviewModalById(id) {
            try {
                const data = await apiRequest(`/documents/${id}`);
                let doc = data.document;
                if (!doc) {
                    doc = state.docs.find(d => d.id === id);
                    if (!doc && state.results.length > 0) {
                        const res = state.results.find(r => r.document && r.document.id === id);
                        if (res) doc = res.document;
                    }
                    if (!doc) return alert('Doc not found');
                }
                state.selected = doc;
                openPreviewModalFor(doc);
            } catch (error) {
                let doc = state.docs.find(d => d.id === id);
                if (!doc && state.results.length > 0) {
                    const res = state.results.find(r => r.document && r.document.id === id);
                    if (res) doc = res.document;
                }
                if (!doc) return alert('Doc not found');
                state.selected = doc;
                openPreviewModalFor(doc);
            }
        }

        function openPreviewModalFor(doc) {
            const overlay = document.createElement('div');
            overlay.className = 'modalOverlay';
            overlay.id = 'previewOverlay';

            const box = document.createElement('div');
            box.className = 'modalBox';

            const docType = doc.document_type || doc.type || 'file';
            const tagsHtml = (doc.tags || []).map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('');
            const likes = doc.likes || 0;
            const reviewsCount = (doc.reviews && doc.reviews.length) || 0;

            box.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-weight:800">${escapeHtml(doc.title || doc.filename)}</div>
        <div class="small">${escapeHtml(doc.subject || '—')} • ${escapeHtml(docType)}</div>
        <div style="margin-top:4px">${tagsHtml}</div>
        <div style="margin-top:4px;display:flex;gap:12px;font-size:12px;color:var(--muted)">
          <span>❤️ ${likes} likes</span>
          <span>💬 ${reviewsCount} reviews</span>
        </div>
      </div>
      <div><button class="btn" onclick="closeModal()">Close</button></div>
    </div>
    <div style="margin-top:10px">
      ${(doc.content && doc.content.length) ?
                    `<pre style="white-space:pre-wrap">${escapeHtml(doc.content)}</pre>` :
                    (doc.blob ?
                        `<iframe src="${doc.blob}" style="width:100%;height:70vh;border:0"></iframe>` :
                        `<div class="small">No extracted text. Backend OCR/indexing required.</div>`
                    )
                }
    </div>
    <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap">
      <button class="btn" onclick="downloadDoc('${doc.id}')">Download</button>
      <button class="like-btn" onclick="likeDocument('${doc.id}')">❤️ ${likes}</button>
    </div>
    
    ${doc.reviews && doc.reviews.length > 0 ? `
      <div style="margin-top:20px">
        <div style="font-weight:700;margin-bottom:12px">User Reviews (${reviewsCount})</div>
        ${doc.reviews.map(review => `
          <div class="review-display">
            <div style="display:flex;justify-content:between;align-items:center;margin-bottom:8px">
              <div class="review-author">${escapeHtml(review.author)}</div>
              <div style="display:flex;align-items:center;gap:4px">
                <span style="color:#f59e0b">${'★'.repeat(review.rating)}${'☆'.repeat(5 - review.rating)}</span>
                <span class="small">${new Date(review.date).toLocaleDateString()}</span>
              </div>
            </div>
            <div class="review-text">${escapeHtml(review.text)}</div>
          </div>
        `).join('')}
      </div>
    ` : `
      <div style="margin-top:20px;text-align:center;padding:20px;color:var(--muted)">
        <div>No reviews yet</div>
        <div class="small">Be the first to share your thoughts!</div>
      </div>
    `}
  `;

            overlay.appendChild(box);
            document.body.appendChild(overlay);
        }

        function closeModal() {
            const el = document.getElementById('previewOverlay');
            if (el) el.remove();
        }

        /* DOWNLOAD */
        function downloadDoc(id) {
            const d = state.docs.find(x => x.id === id);
            if (!d) return alert('Not found');

            if (d.blob) {
                const a = document.createElement('a');
                a.href = d.blob;
                a.download = d.filename || 'file';
                a.click();
            } else {
                const blob = new Blob([d.content || ''], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = d.filename || 'doc.txt';
                a.click();
            }
        }
"""

# Locate indices
idx_render_start = -1
idx_submit_review = -1
idx_fallback_search = -1
idx_bookmark_doc = -1

for i, line in enumerate(lines):
    if 'function renderLibrary(page = 1, highlightId = null) {' in line:
        idx_render_start = i
    if 'async function submitReview(docId) {' in line:
        idx_submit_review = i
    if 'function fallbackSearch(query) {' in line:
        idx_fallback_search = i
    if 'function bookmarkDoc(id) {' in line:
        idx_bookmark_doc = i

if idx_render_start == -1 or idx_submit_review == -1 or idx_fallback_search == -1 or idx_bookmark_doc == -1:
    print("Error: Could not find all anchor points.")
    print(f"renderLibrary: {idx_render_start}")
    print(f"submitReview: {idx_submit_review}")
    print(f"fallbackSearch: {idx_fallback_search}")
    print(f"bookmarkDoc: {idx_bookmark_doc}")
    exit(1)

# Find the end of renderLibrary (approximate, before submitReview)
idx_scroll = -1
for i in range(idx_render_start, idx_submit_review):
    if 'container.scrollIntoView' in lines[i]:
        idx_scroll = i
        break

if idx_scroll == -1:
    print("Error: Could not find scrollIntoView")
    exit(1)

# Construct new lines
new_lines = []
new_lines.extend(lines[:idx_scroll])
new_lines.append(missing_functions_1)
new_lines.extend(lines[idx_submit_review:idx_fallback_search])
new_lines.append(missing_functions_2)
new_lines.extend(lines[idx_bookmark_doc:])

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully repaired teacher.html")
