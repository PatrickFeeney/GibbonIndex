from bs4 import BeautifulSoup

from topic_data import load_topic_data

# generate HTML with links for indexing
topics, par_to_topic, par_texts = load_topic_data(
    "data/gibbon_chapters_topics_lda.csv",
    "data/gibbon_paragraphs_with_topics.csv"
)

soup = BeautifulSoup("<html><head /><body /></html>", 'html.parser')
body = soup.html.body
for i, par_text in enumerate(par_texts):
    for word in topics[par_to_topic[i]]:
        par_text = par_text.replace(word, '<a href="%i">%s</a>' % (i, word))
    # append paragraph tag
    par_tag = BeautifulSoup("<p>%s</p>" % (par_text,), 'html.parser').p
    body.append(par_tag)

with open("output/index_debug.html", "w") as f:
    f.write(soup.prettify())
