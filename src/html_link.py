from bs4 import BeautifulSoup

from topic_data import load_topic_data


topics, par_to_topic, par_texts = load_topic_data(
    "data/gibbon_chapters_topics_lda.csv",
    "data/gibbon_paragraphs_with_topics.csv"
)
topic_word_to_par = [{} for _ in range(topics.shape[0])]
# generate HTML with links for indexing
soup = BeautifulSoup("<html><head /><body /></html>", "html.parser")
body = soup.html.body
for i, par_text in enumerate(par_texts):
    par_topic = par_to_topic[i]
    for word in topics[par_topic]:
        # update each instace of a topic's word with a link
        ind = par_text.lower().find(word)
        while ind != -1:
            start_ind = ind + 1
            if (ind >= 1 and not par_text[ind - 1].isalpha()) and \
               (ind + len(word) < len(par_text) and not par_text[ind + len(word)].isalpha()):
                link_str = '<a href="#topic%i">%s</a>' % \
                    (par_topic, par_text[ind:ind + len(word)])
                par_text = par_text[:ind] + link_str + par_text[ind + len(word):]
                start_ind += len(link_str)
                # record paragraphs with links
                topic_word_to_par[par_topic][word] = \
                    topic_word_to_par[par_topic].get(word, []) + [i]
            ind = par_text.lower().find(word, start_ind)
    # append paragraph tag
    par_tag = BeautifulSoup('<p id="par%i">%s</p>' % (i, par_text,), "html.parser").p
    body.append(par_tag)
# generate index at end of page
for i, topic in enumerate(topics):
    topic_tag = soup.new_tag("h4", id="topic%i" % (i,))
    topic_tag.string = "Topic %i" % (i,)
    body.append(topic_tag)
    for word, pars in topic_word_to_par[i].items():
        word_tag = soup.new_tag("p")
        word_tag.string = word + ": "
        for j, par in enumerate(pars):
            par_tag = soup.new_tag("a", href="#par%i" % (par,))
            par_tag.string = "¶%i" % (par,)
            if j != 0:
                word_tag.append(", ")
            word_tag.append(par_tag)
        body.append(word_tag)

with open("output/index_debug.html", "w") as f:
    f.write(str(soup))
