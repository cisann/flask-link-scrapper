from flask import Flask, request, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Link Scraper</title></head>
<body>
  <h1>Link Scraper</h1>
  <form method="post">
    <input type="url" name="url" placeholder="Enter URL" required>
    <button type="submit">Scrape Links</button>
  </form>
  {% if links %}
  <h2>Found {{ links|length }} links:</h2>
  <ul>
    {% for link in links %}
    <li><a href="{{ link }}">{{ link }}</a></li>
    {% endfor %}
  </ul>
  {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    links = []
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
                if response.status_code >= 400:
                    return jsonify({"error": f"HTTP error: {response.status_code}"}), response.status_code
                content_type = response.headers.get('Content-Type', '')
                if not any(ct in content_type for ct in ('text/html', 'application/xhtml')):
                    return jsonify({"error": "URL did not return HTML content"}), 400
                soup = BeautifulSoup(response.text, 'html.parser')
                base_url = response.url
                for a in soup.find_all('a', href=True):
                    href = a['href'].strip()
                    if not href:
                        continue
                    if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                        continue
                    if href.startswith('//'):
                        scheme = urlparse(base_url).scheme or 'https'
                        full_url = scheme + ':' + href
                        parsed = urlparse(full_url)
                        if parsed.scheme and parsed.netloc:
                            links.append(full_url)
                        continue
                    elif href.startswith(('http://', 'https://')):
                        parsed = urlparse(href)
                        if parsed.scheme and parsed.netloc:
                            links.append(href)
                    else:
                        full_url = urljoin(base_url, href)
                        parsed = urlparse(full_url)
                        if parsed.scheme and parsed.netloc:
                            links.append(full_url)
                links = sorted(set(links))
            except Exception as e:
                return jsonify({"error": str(e)}), 400
    return render_template_string(HTML_TEMPLATE, links=links)

if __name__ == '__main__':
    app.run(debug=True)
