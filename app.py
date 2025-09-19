from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)

CLICKBAIT_WORDS = [
    "shocking", "you won't believe", "unbelievable", "miracle", "secret", "exposed",
    "viral", "trending", "shocker", "can't believe", "mind blown", "what happened next"
]
CREDIBLE_DOMAINS = [
    "nytimes.com", "bbc.com", "theguardian.com", "reuters.com", "apnews.com", "washingtonpost.com",
    "who.int", "nature.com"
]

def analyze_text(text, url=None):
    text = text or ""
    text_lower = text.lower()
    features = {}

    words = re.findall(r"\w+", text)
    features['word_count'] = len(words)

    all_caps = re.findall(r'\b[A-Z]{2,}\b', text)
    features['all_caps_count'] = len(all_caps)

    exclamations = text.count('!')
    questions = text.count('?')
    features['exclamations'] = exclamations
    features['questions'] = questions

    cb_matches = [w for w in CLICKBAIT_WORDS if w in text_lower]
    features['clickbait_matches'] = cb_matches

    numbers = re.findall(r'\d+', text)
    features['numbers_count'] = len(numbers)

    links = re.findall(r'https?://[^\s)]+', text)
    features['links'] = links

    credible_link = False
    for l in links:
        try:
            domain = urlparse(l).netloc.replace('www.', '')
            if any(d in domain for d in CREDIBLE_DOMAINS):
                credible_link = True
        except Exception:
            pass

    if url:
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            if any(d in domain for d in CREDIBLE_DOMAINS):
                credible_link = True
        except Exception:
            pass

    score = 50
    score += min(features['all_caps_count'] * 3, 30)
    score += min((exclamations + questions) * 2, 20)
    score += min(len(cb_matches) * 12, 36)
    score += min(features['numbers_count'] * 1, 10)
    if credible_link:
        score -= 25
    score = max(0, min(100, int(score)))

    if score >= 70:
        verdict = 'High risk of misinformation'
    elif score >= 40:
        verdict = 'Possibly misleading / needs fact-check'
    else:
        verdict = 'Likely credible (still verify important claims)'

    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    flagged = []
    for s in sentences:
        if any(w in s.lower() for w in CLICKBAIT_WORDS) or re.search(r'\b[A-Z]{3,}\b', s):
            flagged.append(s.strip())

    return {
        'score': score,
        'verdict': verdict,
        'features': features,
        'flagged_sentences': flagged,
        'advice': [
            'Check the claim against reputable fact-checkers (e.g., Snopes, FactCheck.org, PolitiFact).',
            'Verify the original source and publication date; look for multiple independent reports.',
            'Be cautious with emotionally charged or sensational language.',
            'If the story seems important, consult primary sources or subject-matter experts.'
        ]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get('text', '').strip()
    url = data.get('url', '').strip()

    if not text and not url:
        return jsonify({'error': 'Please provide text or a URL to analyze.'}), 400

    combined_text = text if text else f'URL only: {url}'
    result = analyze_text(combined_text, url if url else None)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
