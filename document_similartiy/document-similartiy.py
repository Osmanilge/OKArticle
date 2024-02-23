import numpy as np
import pandas as pd 
import PyPDF2
import re
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer


def extract_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""

        for i in range(num_pages):
            page = reader.pages[i]
            text += page.extract_text() + "\n"

        return text
    
def find_abstract_to_references(text):
     # Özet bölümünün başlangıcını ve kaynakça bölümünün sonunu bulmak için regüler ifadeler kullan.
    abstract_start_regex = r"(Abstract|Özet)"
    references_end_regex = r"(References|Kaynakça)"
    # Metinde özetin başlangıcını ve kaynakçanın sonunu bul.
    abstract_start_match = re.search(abstract_start_regex, text, re.IGNORECASE)
    references_end_match = re.search(references_end_regex, text, re.IGNORECASE)
    if abstract_start_match and references_end_match:
        start_index = abstract_start_match.start()
        end_index = references_end_match.end()
        return text[start_index:end_index]
    else:
        return "Abstract veya References bulunamadı."
# PDF dosya yolunu buraya girin
pdf_path = 'article\\TCP_Fairness_Among_Modern_TCP_Congestion_Control_Algorithms_Including_TCP_BBR.pdf'  # Örnek: '/kaggle/input/artcle/Performance_analysis_of_TCP_incast_with_TCP_Lite_and_Abstract_TCP.pdf'
pdf_path2 = 'article\\Performance_analysis_of_TCP_incast_with_TCP_Lite_and_Abstract_TCP.pdf'
pdf_path3 = 'article\\A_Speed_Guide_Model_for_Collision_Avoidance_in_Non-Signalized_Intersections_Based_on_Reduplicate_Game_Theory.pdf'
pdf_path4 = 'article\\Device_to_Device_Communication_using_Stackelberg_Game_Theory_approach.pdf'
pdf_path5 = 'article\\Resource_Allocation_for_Device-to-Device_Communications_Underlaying_Heterogeneous_Cellular_Networks_Using_Coalitional_Games.pdf'  # Örnek: '/kaggle/input/artcle/Performance_analysis_of_TCP_incast_with_TCP_Lite_and_Abstract_TCP.pdf'


full_text_tcp = extract_text(pdf_path)
full_text_tcp2 = extract_text(pdf_path2)
full_text_GT = extract_text(pdf_path3)
full_text_GT2 = extract_text(pdf_path4)
full_text_GT3 = extract_text(pdf_path5)



# Abstract ile References arasındaki metni çıkar
abstract_to_references_tcp = find_abstract_to_references(full_text_tcp)
abstract_to_references_tcp2 = find_abstract_to_references(full_text_tcp2)
abstract_to_references_GT = find_abstract_to_references(full_text_GT)
abstract_to_references_GT2 = find_abstract_to_references(full_text_GT2)
abstract_to_references_GT3 = find_abstract_to_references(full_text_GT3)


sentences = [abstract_to_references_tcp,abstract_to_references_tcp2]
sentences2 = [abstract_to_references_tcp,abstract_to_references_GT]
sentences3 = [abstract_to_references_tcp2,abstract_to_references_GT]
sentences4 = [abstract_to_references_tcp,abstract_to_references_GT2]
sentences5 = [abstract_to_references_tcp2,abstract_to_references_GT2]
sentences6 = [abstract_to_references_GT2,abstract_to_references_GT]
sentences7 = [abstract_to_references_GT2,abstract_to_references_GT3]
sentences8 = [abstract_to_references_GT,abstract_to_references_GT3]
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def calculate_similarity(sentences):
    embeddings = model.encode(sentences)
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return similarity


similarity = calculate_similarity(sentences)
similarity2 = calculate_similarity(sentences2)
similarity3 = calculate_similarity(sentences3)
similarity4 = calculate_similarity(sentences4)
similarity5 = calculate_similarity(sentences5)
similarity6 = calculate_similarity(sentences6)
similarity7 = calculate_similarity(sentences7)
similarity8 = calculate_similarity(sentences8)

print(f"TCP-TCP2 Arası Benzerlik: {similarity}")
print(f"TCP-GT Arası Benzerlik: {similarity2}")    
print(f"TCP2-GT Arası Benzerlik: {similarity3}")
print(f"GT2-GT Arası Benzerlik: {similarity6}")
print(f"GT2-GT3 Arası Benzerlik: {similarity7}")
print(f"GT1-GT3 Arası Benzerlik: {similarity8}")