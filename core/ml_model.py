import re

def predict_spam(text):
    if not text:
        return 0

    text = text.lower()
    score = 0

    spam_words = ["free", "win", "offer", "click", "money", "prize", "urgent", "crypto", "claim"]

    for word in spam_words:
        if word in text:
            score += 0.15

    if "http" in text or "www" in text:
        score += 0.2

    if text.isupper() and len(text) > 5:
        score += 0.2

    if "!!!" in text or "???" in text:
        score += 0.15

    return min(round(score, 2), 1)


def fake_user_score(username):
    if not username:
        return 0

    score = 0
    username = username.lower()

    if len(username) < 4:
        score += 0.2

    if sum(c.isdigit() for c in username) >= 3:
        score += 0.3

    suspicious_words = ["free", "win", "offer", "crypto", "official", "money"]

    for word in suspicious_words:
        if word in username:
            score += 0.2

    if re.search(r"[a-z]+\d{3,}", username):
        score += 0.2

    return min(round(score, 2), 1)


def analyze_url_details(url):
    result = {
        "platform": "Unknown",
        "username": "",
        "risk": 0,
        "reasons": []
    }

    if not url:
        return result

    url_lower = url.lower()

    platforms = {
        "instagram.com": "Instagram",
        "linkedin.com": "LinkedIn",
        "facebook.com": "Facebook",
        "twitter.com": "Twitter",
        "x.com": "X",
        "youtube.com": "YouTube",
        "tiktok.com": "TikTok",
    }

    for domain, platform in platforms.items():
        if domain in url_lower:
            result["platform"] = platform
            result["risk"] += 0.1
            result["reasons"].append(f"Social media link detected: {platform}")
            break

    parts = url.split("/")
    if len(parts) > 3:
        username = parts[3].split("?")[0]
        result["username"] = username

        if any(char.isdigit() for char in username):
            result["risk"] += 0.2
            result["reasons"].append("Username contains numbers")

        if any(word in username.lower() for word in ["free", "win", "crypto", "offer"]):
            result["risk"] += 0.3
            result["reasons"].append("Suspicious username keywords")

    if "?" in url:
        result["risk"] += 0.2
        result["reasons"].append("Tracking parameters detected")

    if any(short in url_lower for short in ["bit.ly", "tinyurl", "goo.gl"]):
        result["risk"] += 0.4
        result["reasons"].append("Shortened URL detected")

    result["risk"] = min(round(result["risk"], 2), 1)
    return result


def calculate_trust(spam, fake):
    risk = spam * 70 + fake * 30
    return round(max(100 - risk, 0), 2)