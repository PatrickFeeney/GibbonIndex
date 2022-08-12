from bisect import bisect

from bs4 import BeautifulSoup
import pandas as pd

from topic_data import load_topic_data


def generate_html(topics, par_to_topic, par_texts, output_path):
    # load data for chapter info
    chapter_df = pd.read_csv("data/gibbon_first_with_titles.csv")
    chapter_titles = list(chapter_df["Titles"])
    chapter_first_pars = list(chapter_df["level_0"])
    # record paragraphs associated with each word in a topic
    topic_word_to_par = [{} for _ in range(topics.shape[0])]
    # generate HTML with links for indexing
    with open("data/html/base.html", "r") as f:
        soup = BeautifulSoup(f, "html.parser")
    body = soup.html.body.div
    chapter_tag = None
    for i, par_text in enumerate(par_texts):
        # handle chapter starts by adding collapsible header
        if chapter_first_pars.count(i) > 0:
            chapter_ind = chapter_first_pars.index(i)
            if chapter_tag is not None:
                body.append(chapter_tag)
            chapter_tag = soup.new_tag("details", id=f"chapter{chapter_ind + 1}")
            chapter_title = soup.new_tag("b")
            chapter_title.string = f"Chapter {chapter_ind + 1}: " + chapter_titles[chapter_ind]
            chapter_summary = soup.new_tag("summary")
            chapter_summary.append(chapter_title)
            chapter_tag.append(chapter_summary)
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
                    link_str = f'<a href="#topic{par_topic}{word}" ' + \
                        'onclick="topicAnchorClick(this)">' + \
                        f'{par_text[ind:ind + len(word)]}' + \
                        f'<sup>{par_topic}</sup></a>'
                    par_text = par_text[:ind] + link_str + par_text[ind + len(word):]
                    start_ind += len(link_str)
                    # record paragraphs with links
                    topic_word_to_par[par_topic][word] = \
                        topic_word_to_par[par_topic].get(word, []) + [i]
                ind = par_text.lower().find(word, start_ind)
        # append paragraph tag
        par_tag = BeautifulSoup('<p id="par%i">%s</p>' % (i, par_text,), "html.parser").p
        chapter_tag.append(par_tag)
    # append last chapter tag
    body.append(chapter_tag)
    # generate index at end of page
    for i, topic in enumerate(topics):
        topic_tag = soup.new_tag("details", id="topic%i" % (i,))
        topic_title = soup.new_tag("b")
        topic_title.string = f"Topic {i} " + \
            f"({sum([len(pars) for pars in topic_word_to_par[i].values()])})"
        topic_summary = soup.new_tag("summary")
        topic_summary.append(topic_title)
        topic_tag.append(topic_summary)
        body.append(topic_tag)
        for word, pars in topic_word_to_par[i].items():
            word_tag = soup.new_tag("p", id=f"topic{i}{word}")
            word_tag.string = word + " (%i): " % (len(pars),)
            for j, par in enumerate(pars):
                par_tag = soup.new_tag("a", href="#par%i" % (par,), onclick="parAnchorClick(this)")
                # create string with chapter then paragraph
                chap_ind = bisect(chapter_first_pars, par) - 1
                chap_par = par - chapter_first_pars[chap_ind] + 1
                par_tag.string = f"§{chap_ind + 1}¶{chap_par}"
                if j != 0:
                    word_tag.append(", ")
                word_tag.append(par_tag)
            topic_tag.append(word_tag)

    with open(output_path, "wb") as f:
        f.write(str(soup).encode('utf8'))


if __name__ == "__main__":
    paths_list = [
        ("data/lda_cleaned_proper_nouns.csv",
         "data/gibbon_paragraphs_with_topics_4_15.csv",
         "docs/index_debug.html"),
        ("data/10_topics/gibbon_tm10_topics.csv",
         "data/10_topics/gibbon_tm10_paragraphs.csv",
         "docs/index_10.html"),
        ("data/25_topics/gibbon_tm25_topics.csv",
         "data/25_topics/gibbon_tm25_paragraphs.csv",
         "docs/index_25.html"),
        ("data/50_topics/gibbon_tm50_topics.csv",
         "data/50_topics/gibbon_tm50_paragraphs.csv",
         "docs/index_50.html"),
        ("data/75_topics/gibbon_tm75_topics.csv",
         "data/75_topics/gibbon_tm75_paragraphs.csv",
         "docs/index_75.html"),
        ("data/100_topics/gibbon_tm100_topics.csv",
         "data/100_topics/gibbon_tm100_paragraphs.csv",
         "docs/index_100.html"),
        ("data/bertopic/gibbon_bertopic_topics.csv",
         "data/bertopic/gibbon_bertopic_paragraphs.csv",
         "docs/index_ber.html"),
    ]
    for topic_path, par_path, output_path in paths_list:
        topics, par_to_topic, par_texts = load_topic_data(topic_path, par_path)
        generate_html(topics, par_to_topic, par_texts, output_path)
