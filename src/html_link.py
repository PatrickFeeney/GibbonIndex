from bs4 import BeautifulSoup

from topic_data import load_topic_data


def generate_html(topics, par_to_topic, par_texts, output_path):
    topic_word_to_par = [{} for _ in range(topics.shape[0])]
    # generate HTML with links for indexing
    soup = BeautifulSoup("<html><head /><body /></html>", "html.parser")
    body = soup.html.body
    for i, par_text in enumerate(par_texts):
        par_topic = par_to_topic[i]
        for word in topics[par_topic]:
            # ignore empty words
            if len(word) == 0:
                continue
            # update each instace of a topic's word with a link
            ind = par_text.lower().find(word)
            while ind != -1:
                start_ind = ind + 1
                if (ind >= 1 and not par_text[ind - 1].isalpha()) and \
                   (ind + len(word) < len(par_text) and not par_text[ind + len(word)].isalpha()):
                    link_str = '<a href="#topic%i">%s<sup>%i</sup></a>' % \
                        (par_topic, par_text[ind:ind + len(word)], par_topic)
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
        topic_tag.string = "Topic %i (%i)" % \
            (i, sum([len(pars) for pars in topic_word_to_par[i].values()]))
        body.append(topic_tag)
        for word, pars in topic_word_to_par[i].items():
            word_tag = soup.new_tag("p")
            word_tag.string = word + " (%i): " % (len(pars),)
            for j, par in enumerate(pars):
                par_tag = soup.new_tag("a", href="#par%i" % (par,))
                par_tag.string = "¶%i" % (par,)
                if j != 0:
                    word_tag.append(", ")
                word_tag.append(par_tag)
            body.append(word_tag)

    with open(output_path, "w") as f:
        f.write(str(soup))


if __name__ == "__main__":
    paths_list = [
        ("data/lda_cleaned_proper_nouns.csv", "data/gibbon_paragraphs_with_topics_4_15.csv", "output/index_debug.html"),
        ("data/10_topics/gibbon_tm10_topics.csv", "data/10_topics/gibbon_tm10_paragraphs.csv", "output/index_10.html"),
        ("data/25_topics/gibbon_tm25_topics.csv", "data/25_topics/gibbon_tm25_paragraphs.csv", "output/index_25.html"),
        ("data/50_topics/gibbon_tm50_topics.csv", "data/50_topics/gibbon_tm50_paragraphs.csv", "output/index_50.html"),
        ("data/75_topics/gibbon_tm75_topics.csv", "data/75_topics/gibbon_tm75_paragraphs.csv", "output/index_75.html"),
        ("data/100_topics/gibbon_tm100_topics.csv", "data/100_topics/gibbon_tm100_paragraphs.csv", "output/index_100.html"),
        ("data/bertopic/gibbon_bertopic_topics.csv", "data/bertopic/gibbon_bertopic_paragraphs.csv", "output/index_ber.html"),
    ]
    for topic_path, par_path, output_path in paths_list:
        topics, par_to_topic, par_texts = load_topic_data(topic_path, par_path)
        generate_html(topics, par_to_topic, par_texts, output_path)
