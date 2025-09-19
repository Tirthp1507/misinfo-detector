const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const copyBtn = document.getElementById('copyReport');
const downloadLink = document.getElementById('downloadReport');
const statusEl = document.getElementById('status');
const resultsEl = document.getElementById('results');
const verdictEl = document.getElementById('verdict');
const scoreEl = document.getElementById('score');
const explanationEl = document.getElementById('explanation');
const flaggedList = document.getElementById('flaggedList');
const adviceList = document.getElementById('adviceList');

function showStatus(msg = "Analyzing…") {
  statusEl.textContent = msg;
  statusEl.classList.remove('hidden');
}
function hideStatus() { statusEl.classList.add('hidden'); }

analyzeBtn.addEventListener('click', async () => {
  const text = document.getElementById('text').value.trim();
  const url = document.getElementById('url').value.trim();
  if (!text && !url) { alert('Please paste text or provide a URL'); return; }

  showStatus(); resultsEl.classList.add('hidden');
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, url })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Server error');
    }
    const data = await res.json();
    populateResults(data);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const urlBlob = URL.createObjectURL(blob);
    downloadLink.href = urlBlob;
    downloadLink.style.display = 'inline-block';
  } catch (e) {
    alert('Error: ' + e.message);
  } finally {
    hideStatus();
  }
});

clearBtn.addEventListener('click', () => {
  document.getElementById('text').value = '';
  document.getElementById('url').value = '';
  resultsEl.classList.add('hidden');
});

copyBtn.addEventListener('click', () => {
  navigator.clipboard.writeText(scoreEl.textContent + " - " + verdictEl.textContent);
  alert("Copied!");
});

function populateResults(data) {
  resultsEl.classList.remove('hidden');
  verdictEl.textContent = data.verdict;
  scoreEl.textContent = data.score;
  explanationEl.textContent =
    "Word count: " + data.features.word_count +
    ", CAPS: " + data.features.all_caps_count +
    ", Numbers: " + data.features.numbers_count +
    ", Links: " + data.features.links.length;

  flaggedList.innerHTML = '';
  (data.flagged_sentences || []).forEach(s => {
    let li = document.createElement('li');
    li.textContent = s;
    flaggedList.appendChild(li);
  });

  adviceList.innerHTML = '';
  (data.advice || []).forEach(a => {
    let li = document.createElement('li');
    li.textContent = a;
    adviceList.appendChild(li);
  });
}
