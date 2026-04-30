from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Small training data (kept minimal)
texts = [
    "win money now",
    "free offer click here",
    "hello friend",
    "let's meet tomorrow"
]

labels = [1, 1, 0, 0]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = MultinomialNB()
model.fit(X, labels)


# ✅ Improved spam detection (ML + rules)
def predict_spam(text):
    text_lower = text.lower()

    # ML probability
    vec = vectorizer.transform([text])
    ml_prob = model.predict_proba(vec)[0][1]

    # Rule-based signals
    score = 0

    spam_keywords = ["win", "free", "money", "offer", "click", "urgent", "prize"]
    keyword_hits = sum(1 for word in spam_keywords if word in text_lower)
    score += keyword_hits * 0.2

    # Extra punctuation
    if "!!!" in text or "???" in text:
        score += 0.1

    # All caps
    if text.isupper():
        score += 0.2

    # Very short text
    if len(text.split()) < 3:
        score += 0.1

    final_score = (0.3 * ml_prob) + (0.7 * min(score, 1))
    return round(min(final_score, 1.0), 2)


# Fake user detection
def fake_user_score(username):
    score = 0

    if len(username) < 4:
        score += 0.3

    if any(char.isdigit() for char in username):
        score += 0.2

    if sum(c.isdigit() for c in username) > 4:
        score += 0.4

    return min(score, 1.0)


# Trust score
def calculate_trust(spam, fake):
    trust = 100 - (spam * 70 + fake * 30)
    return round(max(trust, 0), 2)
def url_score(text):
    score = 0

    if "http" in text or "www" in text:
        score += 0.2

    suspicious_domains = ["bit.ly", "tinyurl", "goo.gl"]
    if any(domain in text for domain in suspicious_domains):
        score += 0.4

    return min(score, 1.0)
def analyze_url_details(url):
    result = {
        "platform": "Unknown",
        "username": "",
        "risk": 0,
        "reasons": []
    }

    if not url:
        return result

    # Detect platform
    if "instagram.com" in url:
        result["platform"] = "Instagram"
    elif "linkedin.com" in url:
        result["platform"] = "LinkedIn"

    # Extract username
    parts = url.split("/")
    if len(parts) > 3:
        result["username"] = parts[3]

    username = result["username"]

    # Username analysis
    if any(char.isdigit() for char in username):
        result["risk"] += 0.2
        result["reasons"].append("Username contains numbers")

    spam_words = ["free", "crypto", "win", "official"]
    if any(word in username.lower() for word in spam_words):
        result["risk"] += 0.3
        result["reasons"].append("Suspicious keywords in username")

    # Query parameter check
    if "?" in url:
        result["risk"] += 0.2
        result["reasons"].append("Contains tracking parameters")

    return result
