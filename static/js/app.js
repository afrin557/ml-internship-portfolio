const $ = (s) => document.querySelector(s);
const launcher = $('#chatLauncher');
const panel = $('#chatPanel');
const closeBtn = $('#chatClose');
const form = $('#chatForm');
const input = $('#chatInput');
const messages = $('#chatMessages');
const suggestions = $('#suggestions');

function toggleChat(open) {
  panel.classList.toggle('open', open);
  panel.setAttribute('aria-hidden', String(!open));
  if (open) input.focus();
}

launcher.addEventListener('click', () => toggleChat(!panel.classList.contains('open')));
closeBtn.addEventListener('click', () => toggleChat(false));

function addMessage(text, role) {
  const el = document.createElement('div');
  el.className = `message ${role}`;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(message) {
  if (!message.trim()) return;
  addMessage(message.trim(), 'user');
  input.value = '';
  suggestions.style.display = 'none';
  addMessage('Thinking…', 'bot');
  const thinking = messages.lastElementChild;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message})
    });
    const data = await response.json().catch(() => ({}));
    thinking.remove();

    if (!response.ok) {
      throw new Error(data.error || 'Chat request failed');
    }

    addMessage(data.reply || 'I could not generate a response.', 'bot');
  } catch (error) {
    thinking.remove();
    addMessage(
      'The assistant could not connect to the AI service. Please try again in a moment.',
      'bot'
    );
  }
}

form.addEventListener('submit', (e) => { e.preventDefault(); sendMessage(input.value); });
suggestions.addEventListener('click', (e) => { if (e.target.tagName === 'BUTTON') sendMessage(e.target.textContent); });

document.querySelector('.nav-toggle').addEventListener('click', (e) => {
  const links = document.querySelector('.nav-links');
  const open = links.classList.toggle('open');
  e.currentTarget.setAttribute('aria-expanded', String(open));
});
document.querySelectorAll('.nav-links a').forEach(a => a.addEventListener('click', () => document.querySelector('.nav-links').classList.remove('open')));
document.querySelector('#year').textContent = new Date().getFullYear();
