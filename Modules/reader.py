from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBox,LTTextContainer, LTChar
from Modules.article_tree import ArticleTree
from enum import Enum
import re

class TitleForm(Enum):
    ROME = 1            #I  Introduction
    ROMEwPOINT_end = 2  #I. Introduction
    NUM = 3             #1  Introduction
    NUMwPOINT_end = 4   #1. Introduction
    TYPELESS = 5

def isTitle(text, titleType):

    #Intiliaze
    partTwo = text
    if(titleType == TitleForm.TYPELESS and len(text.split()) > 1):
        partTwo = text.split()[1]

    if(titleType == TitleForm.TYPELESS and bool(re.match("introduction",partTwo.lower()))):

        pattern = r'([IVX]+(\.[IVX]+)*)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        if(bool(match)):
            return bool(match), TitleForm.ROME
        
        pattern = r'(([IVX]+\.)+)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        if(bool(match)):
            return bool(match), TitleForm.ROMEwPOINT_end
        
        pattern = r'([1-9]+(\.[1-9]+)*)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        if(bool(match)):
            return bool(match), TitleForm.NUM
    
        pattern = r'(([1-9]+\.)+)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        if(bool(match)):
            return bool(match), TitleForm.NUMwPOINT_end

    #After Intiliaze

    if(titleType == TitleForm.ROME):
        pattern = r'([IVX]+(\.[IVX]+)*)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        return bool(match), TitleForm.ROME

    elif(titleType == TitleForm.ROMEwPOINT_end):
        pattern = r'(([IVX]+\.)+)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        return bool(match), TitleForm.ROMEwPOINT_end
    
    elif(titleType == TitleForm.NUM):
        pattern = r'([1-9]+(\.[1-9]+)*)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        return bool(match), TitleForm.NUM
    
    elif(titleType == TitleForm.NUMwPOINT_end):
        pattern = r'(([1-9]+\.)+)\s+[a-zA-Z].*?\n'  
        match = re.match(pattern, text)
        return bool(match), TitleForm.NUMwPOINT_end
    
    return False, TitleForm.TYPELESS

"""
    It is needed for that if title and order of title are divided into to two instance
    Fact: Generally Introduction extracted like that, Reason: Idk
"""
def isTitlewPrev(prevelement, text, titleType):

    #Intiliaze
    if(titleType == TitleForm.TYPELESS and bool(re.match("introduction",text.lower()))):

        pattern = r'([IVX]+(\.[IVX]+)*)\s*?\n'  
        match = re.match(pattern, prevelement)
        if(bool(match)):
            return bool(match), TitleForm.ROME
        
        pattern = r'(([IVX]+\.)+)\s*?\n'  
        match = re.match(pattern, prevelement)
        if(bool(match)):
            return bool(match), TitleForm.ROMEwPOINT_end
        
        pattern = r'([1-9]+(\.[1-9]+)*)\s*?\n'  
        match = re.match(pattern, prevelement)
        if(bool(match)):
            return bool(match), TitleForm.NUM
    
        pattern = r'(([1-9]+\.)+)\s*?\n'  
        match = re.match(pattern, prevelement)
        if(bool(match)):
            return bool(match), TitleForm.NUMwPOINT_end
        

    #After Intiliaze

    if(titleType == TitleForm.ROME):
        pattern = r'([IVX]+(\.[IVX]+)*)\s*?\n'  
        match = re.match(pattern, prevelement)
        return bool(match), TitleForm.ROME

    elif(titleType == TitleForm.ROMEwPOINT_end):
        pattern = r'(([IVX]+\.)+)\s*?\n'  
        match = re.match(pattern, prevelement)
        return bool(match), TitleForm.ROMEwPOINT_end
    
    elif(titleType == TitleForm.NUM):
        pattern = r'([1-9]+(\.[1-9]+)*)\s*?\n'  
        match = re.match(pattern, prevelement)
        return bool(match), TitleForm.NUM
    
    elif(titleType == TitleForm.NUMwPOINT_end):
        pattern = r'(([1-9]+\.)+)\s*?\n'  
        match = re.match(pattern, prevelement)
        return bool(match), TitleForm.NUMwPOINT_end
    
    return False, TitleForm.TYPELESS

def roman_to_int(roman):
    roman_dict = {'I': 1, 'IV': 4, 'V': 5, 'IX': 9, 'X': 10, 'XL': 40, 'L': 50, 'XC': 90, 'C': 100, 'CD': 400, 'D': 500, 'CM': 900, 'M': 1000}
    result = 0
    i = 0
    while i < len(roman):
        if i + 1 < len(roman) and roman[i:i+2] in roman_dict:
            result += roman_dict[roman[i:i+2]]
            i += 2
        else:
            result += roman_dict[roman[i]]
            i += 1
    return result

def int_to_roman(num):
    roman_numerals = {1: 'I', 4: 'IV', 5: 'V', 9: 'IX', 10: 'X', 40: 'XL', 50: 'L', 90: 'XC', 100: 'C', 400: 'CD', 500: 'D', 900: 'CM', 1000: 'M'}
    result = ''
    for value, numeral in sorted(roman_numerals.items(), reverse=True):
        while num >= value:
            result += numeral
            num -= value
    return result

"""
    Purpose: that function checks strictly that did the new title called in correct order. without this function, read work correctly but it makes more correct.
    Side-efffect: if there is possibility one of title missed, then almost all titles related with that title will be gone. it is generally unexpected case.
"""
def isPathNext(path, pathNext, typeOfTitleForm):
    if(path == ""):
        return True

    if(TitleForm.ROMEwPOINT_end == typeOfTitleForm or TitleForm.ROME == typeOfTitleForm):
        Curr = [roman_to_int(x) for x in path.split('.')]
        Next = [roman_to_int(x) for x in pathNext.split('.')]
    elif(TitleForm.NUMwPOINT_end == typeOfTitleForm or TitleForm.NUM == typeOfTitleForm):
        Curr = [int(x) for x in path.split('.')]
        Next = [int(x) for x in pathNext.split('.')]
    else:
        return True

    minimumRange = min(len(Next),len(Curr))
    for i in range(minimumRange-1):
        if(Curr[i] != Next[i]):
            return False
        
    if(Curr[minimumRange - 1] + 1 == Next[minimumRange - 1] or Curr[minimumRange - 1] == Next[minimumRange - 1] and len(Next) > minimumRange and Next[minimumRange] == 1):
        return True
    else:
        return False

    
    

def get_tree_from_article_pdf(pdf_path):
    prevelement = None
    id_path = ""
    title_able = False
    article = None
    TypeOfTitle = TitleForm.TYPELESS
    possibleNameOfArticle =  []
    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            """
                This part gets just texts if you want to get different data, you need to use -isinstance(element, ...)-
            """
            if isinstance(element, LTTextBox):

                if not title_able and len(element.get_text().split('\n')) > 1:
                    possibleNameOfArticle.append([ element.height / (len(element.get_text().split('\n')) - 1), element ])


                if len(element.get_text()) < len("References")+4 and re.match("references",element.get_text().lower()):
                    print("References is detected.")
                    return article
                
                #check is it title?
                is_title, TypeOfTitle = isTitle(element.get_text(),TypeOfTitle)

                is_prev = False
                if not is_title and  prevelement is not None:
                    is_prev, TypeOfTitle = isTitlewPrev(prevelement.get_text(), element.get_text(), TypeOfTitle)
                    is_prev = is_prev and bool(re.match(r'\s*[a-zA-Z].*?\n',element.get_text()))

                if  is_title:
                    temp_id_path = element.get_text().split(" ")[0]
                    temp_id_path = temp_id_path[:-1] if temp_id_path.endswith('.') else temp_id_path
                    if(isPathNext(id_path,temp_id_path,TypeOfTitle)):
                        if not title_able:
                            nameOfArticle = sorted(possibleNameOfArticle, key=lambda x: x[0], reverse=True)[0][1].get_text()
                            article = ArticleTree(re.sub(r'\n', r' ', nameOfArticle))
                            print("Title",re.sub(r'\n', r' ', nameOfArticle))
                            title_able = True

                        id_path = temp_id_path
                        article.add_title_node(id_path, " ".join(element.get_text().split(" ")[1:]))
                        print("girdi2",element)

                elif is_prev and prevelement.y0 == element.y0 and prevelement.y1 == element.y1:
                    temp_id_path = prevelement.get_text()[:-1] 
                    temp_id_path = temp_id_path[:-1] if temp_id_path.endswith('.') else temp_id_path
                    if(isPathNext(id_path,temp_id_path,TypeOfTitle)):
                        if not title_able:
                            nameOfArticle = sorted(possibleNameOfArticle, key=lambda x: x[0], reverse=True)[0][1].get_text()
                            article = ArticleTree(re.sub(r'\n', r' ', nameOfArticle))
                            print("Title",re.sub(r'\n', r' ', nameOfArticle))
                            title_able = True

                        id_path = temp_id_path
                        article.add_title_node(id_path, element.get_text())
                        print("girdi3",prevelement, element)
                #check is it title? end  
                    
                elif id_path != "":
                    article.add_paragraph_node(id_path, element.get_text())
                        
                prevelement = element

            """
                This part gets just texts if you want to get different data, you need to use -isinstance(element, ...)- end
            """


    print("References is NOT detected.")
    return article