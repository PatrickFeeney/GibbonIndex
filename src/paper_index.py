from bisect import bisect

from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd


page_to_chap_par_df = pd.read_csv("data/gibbon_paragraph_to_page.csv", index_col=0)
page_to_chap_par = {page: chap_par for _, (page, chap_par) in page_to_chap_par_df.iterrows()}
chap_par_to_par_df = pd.read_csv("data/gibbon_first_with_titles.csv", index_col=0)
chap_par_to_par = {chap_par: par for _, (par, chap_par) in
                   chap_par_to_par_df[["level_0", "index"]].iterrows()}
chapter_first_pars = list(chap_par_to_par_df["level_0"])
chapter_titles = list(chap_par_to_par_df["Titles"])
par_texts = list(pd.read_csv("data/gibbon_paragraphs_with_topics.csv")["StringText"])
alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q",
            "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]


class IndexEntry():
    def __init__(self, entry_div) -> None:
        self.head = self.elem_to_string(entry_div.find("./{*}head"))
        self.subhs = []
        self.subhs_refs = []
        for p in entry_div.findall("./{*}p"):
            self.subhs += [self.elem_to_string(p)]
            for ref in p.findall("./{*}ref"):
                target = ref.attrib["target"]
                target_vol_page = None
                if ref.attrib["type"] == "volpage":
                    if target.find("-") == -1:
                        target_vol_page = target.split(":")[1]
                    # split targets denoted by hyphen
                    else:
                        # TODO figure out how to denote end paragraph as well
                        # for now just taking start paragraph
                        target_vol_page = target.split("-")[0].split(":")[1]
                elif ref.attrib["type"] == "page":
                    # TODO convert to vol-par? seems to not have enough info
                    pass
                else:
                    raise Exception(f"Unrecognized ref type {ref.attrib['type']}")
                # convert to chap_par then par
                if target_vol_page is not None:
                    target_par = vol_page_to_par(target_vol_page)
                    if target_par is not None:
                        self.subhs_refs += [[target_par]]

    def elem_to_string(self, elem):
        return etree.tostring(
            elem,
            encoding="unicode",
            method="text").strip()

    def index_entry_elem(self, soup: BeautifulSoup):
        word_tag = soup.new_tag("p", id=self.head)
        word_tag.string = self.head
        for i, (subh, subh_refs) in enumerate(zip(self.subhs, self.subhs_refs)):
            # TODO add multiple refs for ranges
            subh_ref = subh_refs
            par_tag = soup.new_tag("a", href="#par%i" % (subh_ref,), onclick="parAnchorClick(this)")
            # create string with chapter then paragraph
            chap_ind = bisect(chapter_first_pars, subh_ref) - 1
            chap_par = subh_ref - chapter_first_pars[chap_ind] + 1
            par_tag.string = f"{subh} §{chap_ind + 1}¶{chap_par}"
            word_tag.append("\t")
            word_tag.append(par_tag)
            if i != 0:
                word_tag.append("\n")
        return word_tag


def vol_page_to_par(vol_page):
    vol, page = vol_page.split("p")
    if int(page) > 1000:  # throw out bad page numbers
        return None
    while vol + "p" + page not in page_to_chap_par:
        page = f"{int(page) - 1:0>3}"
        if int(page) < 0:
            raise Exception(f"Unable to find volume page {vol_page}")
    target_chap_par = page_to_chap_par[vol + "p" + page]
    if "n1" in target_chap_par:  # throw out notes
        return None
    chap, chap_par = target_chap_par.split("pa")
    par = int(chap_par_to_par[chap + "pa01"]) + int(chap_par) - 1
    return par


def generate_html(index_entries, output_path):
    par_to_page = {vol_page_to_par(page): page for page, _ in page_to_chap_par.items()}
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
        # append horizontal line if start of new page
        if i in par_to_page:
            chapter_tag.append(soup.new_tag("hr"))
        # append paragraph tag
        par_tag = BeautifulSoup('<p id="par%i">%s</p>' % (i, par_text,), "html.parser").p
        chapter_tag.append(par_tag)
    # append last chapter tag
    body.append(chapter_tag)
    # generate index at end of page
    cur_start_char = ""
    for i, index_entry in enumerate(index_entries):
        # add new heading for new each character
        new_start_char = index_entry.head[0].upper()
        # checks that it follows alphabetical ordering and subsequent entry matches change
        if cur_start_char == "" or \
                (new_start_char != cur_start_char and
                 new_start_char in alphabet and
                 alphabet.index(new_start_char) - alphabet.index(cur_start_char) == 1 and
                 i < len(index_entries) - 1 and
                 new_start_char == index_entries[i + 1].head[0].upper()):
            cur_start_char = new_start_char
            cur_char_tag = soup.new_tag("details")
            cur_char_title = soup.new_tag("b")
            cur_char_title.string = cur_start_char
            cur_char_summary = soup.new_tag("summary")
            cur_char_summary.append(cur_char_title)
            cur_char_tag.append(cur_char_summary)
            body.append(cur_char_tag)
        # add index entry
        entry_tag = soup.new_tag("div", id=f"{cur_start_char}_{i}")
        entry_tag_head = soup.new_tag("p", style="margin-bottom: 0;")
        entry_tag_head.string = index_entry.head
        entry_tag.append(entry_tag_head)
        for subheader, subheader_refs in zip(index_entry.subhs, index_entry.subhs_refs):
            subheader_ref = subheader_refs[0]
            par_tag = soup.new_tag("a", href="#par%i" % (subheader_ref,),
                                   style="text-indent: 1em; display: inline-block;",
                                   onclick="parAnchorClick(this)")
            # create string with chapter then paragraph
            chap_ind = bisect(chapter_first_pars, subheader_ref) - 1
            chap_par = subheader_ref - chapter_first_pars[chap_ind] + 1
            par_tag.string = f"{subheader} §{chap_ind + 1}¶{chap_par}"
            entry_tag.append(par_tag)
            entry_tag.append(soup.new_tag("br"))
        cur_char_tag.append(entry_tag)
    # write output
    with open(output_path, "wb") as f:
        f.write(str(soup).encode('utf8'))


if __name__ == "__main__":
    tree = etree.parse("data/gibbon-bury-newyork1906-index-ner.xml")
    entry_divs = tree.findall("./{*}text/{*}body/{*}div/{*}div[@subtype='entry']")
    index_entries = [IndexEntry(entry_div) for entry_div in entry_divs]
    generate_html(index_entries, "docs/index_paper.html")
