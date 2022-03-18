from bs4 import BeautifulSoup

from topic_data import load_topic_data

# generate HTML with links for indexing
topics, par_to_topic, par_texts = load_topic_data(
    "data/gibbon_chapters_topics_lda.csv",
    "data/gibbon_paragraphs_with_topics.csv"
)

soup = BeautifulSoup("<html><head /><body /></html>", "html.parser")
body = soup.html.body
for i, par_text in enumerate(par_texts):
    for word in topics[par_to_topic[i]]:
        link_str = '<a href="%i">%s</a>' % (i, word)
        ind = par_text.lower().find(word)
        while ind != -1:
            start_ind = ind + 1
            if (ind >= 1 and not par_text[ind - 1].isalpha()) and \
               (ind + len(word) < len(par_text) and not par_text[ind + len(word)].isalpha()):
                par_text = par_text[:ind] + link_str + par_text[ind + len(word):]
                start_ind += len(link_str)
            ind = par_text.lower().find(word, start_ind)
    # append paragraph tag
    par_tag = BeautifulSoup("<p>%s</p>" % (par_text,), "html.parser").p
    body.append(par_tag)

with open("output/index_debug.html", "w") as f:
    f.write(soup.prettify())

# TODO index page (topic with subheadings for each word, linking to each paragraph for word)
