from flask import Flask, request, render_template_string, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head><title>Link Scraper</title></head>
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
        url = request.form.get('url')
        if url:
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, timeout=10, headers=headers, allow_redirects=True)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                base_url = url
                for a in soup.find_all('a', href=True):
                    href = a['href'].strip()
                    if not href:
                        continue
                    if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                        continue
                    if href.startswith('//'):
                        href = 'https:' + href
                        links.append(href)
                        continue
                    elif href.startswith('http://') or href.startswith('https://'):
                        parsed = urlparse(href)
                        if parsed.scheme and parsed.netloc:
                            links.append(href)
                    else:
                        full_url = urljoin(base_url, href)
                        links.append(full_url)
                links = sorted(set(links))
            except Exception as e:
                return f"Error: {str(e)}", 400
    return render_template_string(HTML_TEMPLATE, links=links)

if __name__ == '__main__':
    app.run(debug=True)
