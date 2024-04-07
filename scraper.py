import requests
import re
from bs4 import BeautifulSoup
import time
from data import *
from trash_can import *
import threading


"""
These are the good functions that I am very happy with
"""
def remove_parentheses(text):
  return re.sub(r"\(([^)]+)\)", '', text).strip()

def get_book_names(text):
  results = re.findall(r"\d*\s*[a-z,A-Z,D&C]+\.*", text)
  for i in range(len(results)):
    results[i] = results[i].strip()
    results[i] = re.sub(r'\s', ' ', results[i])
  return results

def get_CR_references(text):

  if text == '' or text == ' ':
    return []
  
  text = remove_parentheses(text)
  books = get_book_names(text)

  text_divided = re.split(r"\d*\s*[a-z,A-Z,D&C]+\.*", text)[1:]

  CRs = []

  for i in range(len(text_divided)):

    text_divided[i] = text_divided[i].replace('.', '')
    text_divided[i] = text_divided[i].strip()

    sub_refs = text_divided[i].split(';')

    #$#print(f'subref = {sub_refs}')

    for j in range(len(sub_refs)):
      if sub_refs[j] == '':
        continue

      sub_refs[j] = sub_refs[j].replace(':', '_')
      sub_refs[j] = sub_refs[j].strip()

      markdown_ref = f'[[{books[i]} {sub_refs[j]}]]'

      #$#print(markdown_ref)

      CRs.append(markdown_ref)
  return CRs  

def get_TG_references(text):

  if text == ' ' or text == '':
    return []
  
  TGs = []

  refs = text.split(';')
  for i in range(len(refs)):

    if refs[i] == ' ' or refs[i] == '':
      continue

    refs[i] = refs[i].strip()
    refs[i] = refs[i].replace(',','')
    refs[i] = refs[i].replace(' ', '_')
    refs[i] = refs[i].replace('.', '')

    markdown_tag = f" #{refs[i]} "

    TGs.append(markdown_tag)

  #$#print(TGs)
  return TGs

def get_references(li):
  CR_list: list
  TG_list: list
  
  # text= li.get_text()
  text = li
  
  if text.find('TG') != -1:

    CRs, TGs = text.split('TG')

    CR_list = get_CR_references(CRs)
    TG_list = get_TG_references(TGs)
  else:

    CRs = text

    CR_list = get_CR_references(CRs)
    TG_list = []

  return CR_list + TG_list

def get_reference_string(li):
  markdown_links = get_references(li)
  ref_string = '('
  for i in range(len(markdown_links)):
    ref_string += markdown_links[i]
  # for i in range(len(ref_string)):
  #   if i > len(markdown_links):
  #     break
  #   ref_string += markdown_links[i]
  ref_string += ')'
  return ref_string

def get_note_id(a_tag):
  ref = a_tag.get('href')
  return ref[ref.find('#')+1:]

def generate_bofm_urls():
  urls = []
  for book in map_book_to_chapter_number:
    for i in range(1, map_book_to_chapter_number[book]+1):
      url = f'https://www.churchofjesuschrist.org/study/scriptures/bofm/{book}/{i}'
      urls.append((url, map_url_to_file_name[book], i))
  return urls

def generate_ot_urls():
  urls = []
  for book in map_ot_book_to_chapter_number:
    for i in range(1, map_ot_book_to_chapter_number[book]+1):
      url = f'https://www.churchofjesuschrist.org/study/scriptures/ot/{book}/{i}'
      urls.append((url, map_ot_url_to_file_name[book], i))
  return urls

def generate_urls(volume, mapping_chapter_num, mapping_file_name):
  urls = []
  for book in mapping_chapter_num:
    for i in range(136, mapping_chapter_num[book]+1):
      url = f'https://www.churchofjesuschrist.org/study/scriptures/{volume}/{book}/{i}'
      urls.append((url, mapping_file_name[book], i))
  return urls


"""
I don't love these functions nearly as much as 
"""
def get_book_name_from_ref(string, previous_book_name):
  # Check if the references is only a chapter and a verse
  result = re.search(r"^\d*\s*[A-Za-z]+\.", string)
  if result:
    # return an empty string to signify to the calling function that they should use the most recent book_name
    return result.string
  # Check if the reference has a weird space character indicating that it is a book like 1 Kgs., 1 Ne., etc.
  return string[:string.find(' ')]

def replace_a_tag_with_word_and_reference(a, references):
  rtrn_str = a.get_text()[1:]
  reference_str = '('
  for reference in references:
    clean_reference = reference.replace(':', '_')
    reference_str += f'[[{clean_reference}]],'
  rtrn_str = rtrn_str + ' ' + reference_str[:-1] + ')'
  return rtrn_str

def replace_a_tag_with_word_and_reference_V2(a, crs, tgs):
  rtrn_str = a.get_text()[1:]
  reference_str = '('
  for cr in crs:
    clean_reference = cr.replace(':', '_')
    reference_str += f'[[{clean_reference}]], '
  rtrn_str = rtrn_str + ' ' + reference_str[:-1] + ', '
  for tg in tgs:
    rtrn_str += tg + ', '
  return rtrn_str[:-2] + ')'

def get_associated_references_V2(li_element):
  #$#print(li_element.get_text())
  a_text_list = []
  book_name = ''
  for a_tag in li_element.find_all("a"):
    a_text = a_tag.get_text()
    # Replace unrecognized characters from the beginning of the string
    a_text = a_text.replace('\xa0', ' ')
    # Get rid of parentheses that indicate the reference is referring to more than one verse
    paren_pattern = r"\(([^)]+)\)"
    a_text = re.sub(paren_pattern, '', a_text)
    # Get rid of trailing whitespace
    a_text = a_text.strip()
    # Get the book name
    # book_name = get_book_name_from_ref(a_text, book_name)
    # if not a_text.find(book_name):
    #   a_text = book_name + ' ' + a_text
    # Add the text to the list
    a_text_list.append(a_text)
  return a_text_list


def modify_verse_html_for_writing_to_file_V2(paragraph, soup):
  for a_tag in paragraph.find_all("a"):
    note_id = get_note_id(a_tag)

    li = soup.find(attrs={"id" : note_id}).get_text()

    markdown_reference_string = get_reference_string(li)

    a_tag.string = a_tag.get_text()[1:] + ' ' + markdown_reference_string

    # crs, tgs = return_references_as_strings_and_tags(soup.find(attrs={"id" : note_id}).get_text())
    # a_tag.string = replace_a_tag_with_word_and_reference_V2(a_tag, crs, tgs)
  return paragraph

def create_notes_for_chapter_V2(url, path):

  response = requests.get(url[0])

  soup = BeautifulSoup(response.content, "html.parser")

  body_block = soup.find("div", class_="body-block")
  book_name = url[1]
  chapter = url[2]

  for paragraph in body_block.find_all("p"):

    new_paragraph = modify_verse_html_for_writing_to_file_V2(paragraph, soup)

    verse_number = new_paragraph.find("span", class_='verse-number').get_text()
    verse_number = verse_number.strip()
    with open(f"{path}/{book_name} {chapter}_{verse_number}.md", "w") as verse_file:
      verse_file.write(new_paragraph.get_text().replace('\u2161', ''))
  print(f'{book_name} {chapter}')

def run(urls, path):
  start_time = time.time()
  for url in urls:
    create_notes_for_chapter_V2(url, path)
    #$#print(url[1] + ' ' + str(url[2]))
  end_time = time.time()
  #$#print(f'Total time = {str(end_time - start_time)}')

def run_V2(urls, path):
    num_threads = 10
    chunk_size = len(urls) // num_threads

    threads = []
    start_time = time.time()

    for i in range(num_threads):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < num_threads - 1 else len(urls)
        thread = threading.Thread(target=process_url_range, args=(urls, path, start_idx, end_idx))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    print(f'Total time = {end_time - start_time:.2f} seconds')

# bofm_urls = generate_bofm_urls()
# run(bofm_urls, 'bofm_notes')
# ot_urls = generate_ot_urls()
# ot_urls =generate_urls('ot', map_ot_book_to_chapter_number, map_ot_url_to_file_name)
# nt_urls = generate_urls('nt', map_nt_book_to_chapter_number, map_nt_url_to_file_name)
# run(nt_urls, 'nt_notes')
dc_urls = generate_urls('dc-testament', map_dc_book_to_chapter_number, map_dc_url_to_file_name)
run(dc_urls, 'dc_notes')
# run(ot_urls, 'ot_notes')
