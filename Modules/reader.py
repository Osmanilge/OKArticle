from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox,LTTextContainer, LTChar
from Modules.article_tree import ArticleTree
import re

def find_pre_pattern(text):
    pattern = r'[1-9](\.[1-9])*\n'  # Aradığınız regex deseni
    match = re.match(pattern, text)
    return bool(match)

def find_custom_pattern(text):
    pattern = r'[1-9](\.[1-9])*\s[a-zA-Z].*?\n'  # Güncellenmiş regex deseni
    match = re.match(pattern, text)
    return bool(match)

def get_tree_from_article_pdf(pdf_path):
    prevelement = None
    id_path = ""
    title_able = False
    article = None
    
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            """
                This part gets just texts if you want to get different data, you need to use -isinstance(element, ...)-
            """
            if isinstance(element, LTTextBox):
                if not title_able:
                    article = ArticleTree(element.get_text())
                    title_able = True
                else:
                    #check is it title?
                    if find_custom_pattern(element.get_text()):
                        id_path = element.get_text().split(" ")[0]
                        article.add_title_node(id_path, " ".join(element.get_text().split(" ")[1:]))
        
                    elif prevelement is not None and find_pre_pattern(prevelement.get_text()) and prevelement.y0 == element.y0 and prevelement.y1 == element.y1:
                        id_path = prevelement.get_text()[:-1] 
                        article.add_title_node(id_path, element.get_text())
                    #check is it title? end

                    #check Introduction is seen before get the paragraph to tree  
                    elif id_path != "":
                        article.add_paragraph_node(id_path, element.get_text())
                    #check Introduction is seen before get the paragraph to tree  end
                        
                prevelement = element

            """
                This part gets just texts if you want to get different data, you need to use -isinstance(element, ...)- end
            """



    return article