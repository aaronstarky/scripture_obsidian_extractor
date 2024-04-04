#TODO: deprecate
def return_references_as_strings_and_tags(li):
    # Find out if there are topical guide entries
    # string = li.get_text()
    string = li
    find_result = string.find('TG')
    if find_result == 0:
        rtrn_list = []
        string = string[3:]
        tgs = string.split(';')
        for tg in tgs:
            new_tg = '#' + tg.replace(' ', '_')
            rtrn_list.append(new_tg)
        return [], rtrn_list
    if find_result == -1:
        rtrn_list = []
        crs = string.split(';')
        result = re.search(r"^\d*\s*[A-Za-z]+\.", crs[0])
        curr_book_name = ''
        if result is not None:
          curr_book_name = result.string
        # curr_book_name = re.search(r"^\d*\s*[A-Za-z]+\.", crs[0]).string
        for cr in crs:
            new_cr = cr
            if not re.search(r"^\d*\s*[A-Za-z]+\.", crs[0]):
                new_cr = curr_book_name + ' ' + cr
            rtrn_list.append(new_cr)
        return rtrn_list, []
    else:
        l = string.split('TG')
        crs = l[0].split(';')
        rtrn_list1 = []
        curr_book_name = ''
        result = re.search(r"^\d*\s*[A-Za-z]+\.*", crs[0])
        if result is not None:
          curr_book_name = result.string
        # curr_book_name = re.search(r"^\d*\s*[A-Za-z]+\.", crs[0]).string
        for cr in crs:
            new_cr = re.sub(r"\(([^)]+)\)", '', cr).strip()
            if re.search(r"^\d*:\d*", new_cr):
                print('found a scripture with refs')
                new_cr = curr_book_name + ' ' + cr
            else:
                print()
                curr_book_name = re.search(r"^\d*\s*[A-Za-z]*\.*", new_cr).string
                curr_book_name = re.sub(r"\s\d*:\d*", '', curr_book_name)
            new_cr = new_cr.strip()
            # if new_cr[-1] == '.':
            #     new_cr = new_cr[:-1]
            rtrn_list1.append(new_cr)
        tgs = l[1].split(';')
        rtrn_list2 = []
        for tg in tgs:
            new_tg = '#' + tg.replace(' ', '_').replace(',', '')
            # if new_tg[-1] == '.':
            #     new_tg = new_tg[:-1]

            rtrn_list2.append(new_tg)
        return rtrn_list1, rtrn_list2
    
def modify_verse_html_for_writing_to_file(paragraph, soup):
  for a_tag in paragraph.find_all("a"):
    note_id = get_note_id(a_tag)
    references = get_associated_references_V2(soup.find(attrs={"id" : note_id}))
    # a_tag.string = replace_a_tag_with_word_and_reference(a_tag, references)
  return paragraph