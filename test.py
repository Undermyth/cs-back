import markdown
from bs4 import BeautifulSoup
f = open("/home/csy/cs-site/mynotes/hello/blog.md")
html = markdown.markdown(f.read())
soup = BeautifulSoup(html, 'lxml')
log_entries = soup.find_all('p')

print("Number of entries:", len(log_entries))
