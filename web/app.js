/**
 * Importance — Customs Clearance Documentation Assistant
 * InsForge AI-powered frontend
 */

// ─── Configuration ──────────────────────────────────────────────────
const INSFORGE_BASE_URL = 'https://f3vvh546.us-east.insforge.app';
const INSFORGE_API_KEY = 'ik_238c8307220697c26999f7b16d6cbeae';
const AI_MODEL = 'google/gemini-3.1-pro-preview';

const SYSTEM_PROMPT = `You are an expert customs clearance consultant and documentation specialist.
Your role is to help users prepare customs clearance documentation for importing products.

When a user asks about a product, provide:

1. **HS Code Suggestions** — Give the most likely Harmonized System (HS) tariff codes for the product,
   with a brief explanation of each code.

2. **Required Customs Forms** — List the specific forms needed (CBP 7501, CBP 3461, ISF 10+2, etc.)
   and briefly explain what each one is for.

3. **Regulatory Requirements** — Mention any relevant agencies (FDA, USDA APHIS, EPA, CPSC, FCC, etc.)
   and permits/licenses required.

4. **Duty & Tax Information** — Provide estimated duty rates for the HS codes and mention any
   applicable trade agreements or preferential tariffs.

5. **Step-by-Step Clearance Process** — Walk the user through the import clearance steps for this
   specific product.

6. **Common Pitfalls** — Warn about typical documentation mistakes or compliance issues for the product.

Always be precise, practical, and cite specific form numbers and regulations.
If you're unsure about something, say so rather than guessing.
Format your responses with clear headings and bullet points for readability.`;


// ─── State ──────────────────────────────────────────────────────────
let chatHistory = [];
let isProcessing = false;
let insforge = null;


// ─── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initInsForge();
  bindEvents();
});


function initInsForge() {
  try {
    if (typeof InsForge !== 'undefined' && InsForge.createClient) {
      insforge = InsForge.createClient({
        baseUrl: INSFORGE_BASE_URL,
        anonKey: INSFORGE_API_KEY,
      });
      setStatus(true);
    } else {
      console.warn('InsForge SDK not loaded, falling back to fetch API');
      setStatus(true); // We'll use fetch fallback
    }
  } catch (e) {
    console.error('InsForge init error:', e);
    setStatus(true); // Use fetch fallback
  }
}


function setStatus(connected) {
  const dot = document.querySelector('.status-dot');
  const text = document.querySelector('.status-text');
  if (connected) {
    dot.className = 'status-dot connected';
    text.textContent = 'AI Connected';
  } else {
    dot.className = 'status-dot disconnected';
    text.textContent = 'AI Offline';
  }
}


// ─── Events ─────────────────────────────────────────────────────────
function bindEvents() {
  // Send
  document.getElementById('sendBtn').addEventListener('click', () => sendMessage());
  document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  // Generate
  document.getElementById('generateBtn').addEventListener('click', generateFromSidebar);

  // Clear
  document.getElementById('clearBtn').addEventListener('click', clearConversation);

  // Sample prompts
  document.querySelectorAll('.sample-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('chatInput').value = btn.dataset.prompt;
      sendMessage();
    });
  });

  // Mobile sidebar
  document.getElementById('mobileSidebarBtn').addEventListener('click', () => {
    document.getElementById('sidebar').classList.add('open');
  });
  document.getElementById('sidebarToggle').addEventListener('click', () => {
    document.getElementById('sidebar').classList.remove('open');
  });
}


// ─── Generate from sidebar ─────────────────────────────────────────
function generateFromSidebar() {
  const name = document.getElementById('productName').value.trim();
  const desc = document.getElementById('productDesc').value.trim();
  const origin = document.getElementById('originCountry').value.trim();
  const dest = document.getElementById('destCountry').value.trim();

  if (!name) { alert('Please enter a product name.'); return; }

  let prompt = `I need customs clearance documentation for importing **${name}**.`;
  if (desc) prompt += ` Product description: ${desc}.`;
  if (origin) prompt += ` Country of origin: ${origin}.`;
  if (dest) prompt += ` Destination: ${dest}.`;
  prompt += ' Please provide a comprehensive customs clearance documentation guide.';

  document.getElementById('chatInput').value = prompt;
  sendMessage();

  // Close mobile sidebar
  document.getElementById('sidebar').classList.remove('open');
}


// ─── Send Message ───────────────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text || isProcessing) return;

  input.value = '';
  isProcessing = true;
  toggleUI(false);

  // Hide empty state
  const emptyState = document.getElementById('emptyState');
  if (emptyState) emptyState.style.display = 'none';

  // Add user message
  chatHistory.push({ role: 'user', content: text });
  appendMessage('user', text);

  // Show thinking indicator
  const thinkingEl = appendThinking();

  try {
    const response = await getAIResponse(text);
    thinkingEl.remove();
    chatHistory.push({ role: 'assistant', content: response });
    appendMessage('assistant', response);
  } catch (err) {
    thinkingEl.remove();
    const errorMsg = `⚠️ **Error:** ${err.message}`;
    appendMessage('assistant', errorMsg);
  }

  isProcessing = false;
  toggleUI(true);
  scrollToBottom();
}


// ─── AI Response via fetch ──────────────────────────────────────────
async function getAIResponse(userMessage) {
  // Build messages array
  const messages = [
    { role: 'system', content: SYSTEM_PROMPT },
    ...chatHistory.map(m => ({ role: m.role, content: m.content })),
  ];

  // Use InsForge SDK if available, otherwise fetch
  if (insforge && insforge.ai) {
    try {
      const completion = await insforge.ai.chat.completions.create({
        model: AI_MODEL,
        messages,
        temperature: 0.7,
        maxTokens: 4000,
      });
      // SDK may return { choices } or { text }
      if (completion.choices && completion.choices[0]) {
        return completion.choices[0].message.content;
      }
      if (completion.text) {
        return completion.text;
      }
      return JSON.stringify(completion);
    } catch (sdkErr) {
      console.warn('SDK call failed, trying fetch fallback:', sdkErr);
    }
  }

  // Fetch fallback using correct InsForge endpoint
  const res = await fetch(`${INSFORGE_BASE_URL}/api/ai/chat/completion`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${INSFORGE_API_KEY}`,
    },
    body: JSON.stringify({
      model: AI_MODEL,
      messages,
      temperature: 0.7,
      max_tokens: 4000,
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }

  const data = await res.json();
  // InsForge returns { text, metadata }
  if (data.text) return data.text;
  // OpenAI-style fallback
  if (data.choices && data.choices[0]) return data.choices[0].message.content;
  return JSON.stringify(data);
}


// ─── DOM helpers ────────────────────────────────────────────────────
function appendMessage(role, content) {
  const container = document.getElementById('messages');
  const avatar = role === 'user' ? '👤' : '📦';

  const el = document.createElement('div');
  el.className = `message ${role}`;
  el.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">${renderMarkdown(content)}</div>
  `;
  container.appendChild(el);
  scrollToBottom();
}


function appendThinking() {
  const container = document.getElementById('messages');
  const el = document.createElement('div');
  el.className = 'message assistant';
  el.innerHTML = `
    <div class="message-avatar">📦</div>
    <div class="message-content">
      <div class="thinking">
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
      </div>
    </div>
  `;
  container.appendChild(el);
  scrollToBottom();
  return el;
}


function scrollToBottom() {
  const chatArea = document.getElementById('chatArea');
  requestAnimationFrame(() => { chatArea.scrollTop = chatArea.scrollHeight; });
}


function toggleUI(enabled) {
  document.getElementById('sendBtn').disabled = !enabled;
  document.getElementById('chatInput').disabled = !enabled;
  document.getElementById('generateBtn').disabled = !enabled;
}


function clearConversation() {
  chatHistory = [];
  document.getElementById('messages').innerHTML = '';
  const emptyState = document.getElementById('emptyState');
  if (emptyState) emptyState.style.display = '';
}


// ─── Minimal Markdown Renderer ──────────────────────────────────────
function renderMarkdown(text) {
  if (!text) return '';

  let html = escapeHTML(text);

  // Code blocks
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Headings
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Unordered lists
  html = html.replace(/^\s*[-*] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
  // Fix nested ul
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  // Ordered lists
  html = html.replace(/^\s*\d+\.\s+(.+)$/gm, '<li>$1</li>');

  // Tables
  html = html.replace(/^\|(.+)\|$/gm, (match, content) => {
    const cells = content.split('|').map(c => c.trim());
    if (cells.every(c => /^[-:]+$/.test(c))) return ''; // separator row
    const tag = 'td';
    return '<tr>' + cells.map(c => `<${tag}>${c}</${tag}>`).join('') + '</tr>';
  });
  html = html.replace(/(<tr>[\s\S]*?<\/tr>)/g, '<table>$1</table>');
  html = html.replace(/<\/table>\s*<table>/g, '');

  // Paragraphs (double newlines)
  html = html.replace(/\n\n+/g, '</p><p>');
  html = html.replace(/\n/g, '<br>');

  // Wrap in paragraph if not starting with block element
  if (!/^<(h[1-4]|ul|ol|pre|table|p)/.test(html)) {
    html = '<p>' + html + '</p>';
  }

  return html;
}


function escapeHTML(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
