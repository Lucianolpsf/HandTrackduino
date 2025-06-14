# Cache em memória
import requests
import qrcode
import base64
from io import BytesIO

NICKS = ["lucianolpsf", "fernandallobao", "jesieldossantos", "Victorrezende19", "calebegomes740", "CaioHarrys", "aucelio0", "brunofluna", "Rafael-ai13", "Xandy77", "pauloalvezz" ]
github_cache = {}

def get_github_user_info(username):
    if username in github_cache:
        return github_cache[username]
    url = f"https://api.github.com/users/{username}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        info = {
            "username": username,
            "name": data.get("name") or username,
            "avatar_url": data.get("avatar_url"),
            "profile_url": data.get("html_url")
        }
        github_cache[username] = info  # Salva no cache
        return info
    return None

def generate_qr_code(url):
    qr = qrcode.make(url)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Exemplo de lista de nicks

def get_cards():
    cards = []
    for nick in NICKS:
        info = get_github_user_info(nick)
        if info:
            info["qr_code"] = generate_qr_code(info["profile_url"])
            cards.append(info)
    return cards