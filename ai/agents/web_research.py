import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ===== SEARCH (REAL RESULTS) =====
def search_duckduckgo(query):
    url = "https://html.duckduckgo.com/html/"

    res = requests.post(url, data={"q": query}, headers=HEADERS, timeout=10)

    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for a in soup.select(".result__a")[:5]:
        href = a.get("href")
        if href:
            results.append(href)

    return results


# ===== FETCH PAGE CONTENT =====
def fetch_page(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)

        soup = BeautifulSoup(res.text, "html.parser")

        paragraphs = soup.find_all("p")

        text = " ".join(p.get_text() for p in paragraphs[:10])

        return text[:1500]  # token control

    except:
        return ""


# ===== MAIN SEARCH FUNCTION =====
def web_search(query):
    try:
        urls = search_duckduckgo(query)

        content = ""

        for url in urls[:3]:
            page = fetch_page(url)
            if page:
                content += f"\nSOURCE: {url}\n{page}\n"

        return content.strip()

    except Exception:
        return ""