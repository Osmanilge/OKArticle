from transformers import pipeline
from transformers import SummarizationPipeline

def count_words(text):
    words = text.split()
    return len(words)

class ArticleTree:
    def __init__(self, title):
        self.root = Node(0,"",title)

    def add_paragraph_node(self, id_path, data):
        self.root.add_paragraph_node(id_path, data)

    def add_title_node(self, id_path, data):
        self.root.add_title_node( id_path, data)

    def print_article_tree(self):
        self.root.print_article_tree("")

class Node:
    def __init__(self, depth, id, data):
        self.depth = depth
        self.id = id
        self.data = data.replace("-\n", "").replace("\n", " ")
        self.children = []
        self.summarizeText = None
        self.countOfWords = 0

    def add_title_node(self, id_path, data):
        ids = id_path.split(".")
        if len(ids) > 1:
            for child in self.children:
                if child.id == ids[0]:
                    child.add_title_node(".".join(ids[1:]) ,data)
                    break
        else:
            newChild = Node(self.depth + 1, ids[0], data)
            self.children.append(newChild)

    def add_paragraph_node(self, id_path, data):
        ids = id_path.split(".")
        if ids[0] != "":
            for child in self.children:
                if child.id == ids[0]:
                    child.add_paragraph_node(".".join(ids[1:]) ,data)
                    break
        else:
            newChild = Node(self.depth + 1, None, data)
            self.children.append(newChild)

    def print_article_tree(self, path):
        print(path," ",self.data)
        for child in self.children:
            child.print_article_tree(path+".")

    def calculate_count_of_words(self):
        totalCount = 0
        if self.id is not None:
            for child in self.children:
                totalCount += child.calculate_count_of_words()
        else:
            totalCount = count_words(self.data)

        self.countOfWords = totalCount
        return totalCount

    def print_count_words(self, path):
        print(path," ",self.countOfWords)
        if self.countOfWords < 7:
            print(self.data)
            
        for child in self.children:
            child.print_count_words(path+".")

    def summarize_article(self, summarize_length, Summarizer, elasticityOfLength = 0.1):

        if self.id is not None:
            allText = ""
            for child in self.children:
                allText += child.summarize_article(int(1000*child.countOfWords/self.countOfWords), Summarizer, elasticityOfLength) + "\n\n"

            if summarize_length < self.countOfWords:
                self.summarizeText = Summarizer(self.data, max_length=summarize_length, min_length=summarize_length*(1 - elasticityOfLength), do_sample=False) 
            else:
                self.summarizeText = self.data

            return self.summarizeText 
            
        else:
            if summarize_length < self.countOfWords:
                self.summarizeText = Summarizer(self.data, max_length=summarize_length, min_length=summarize_length*(1 - elasticityOfLength), do_sample=False) 
            else:
                self.summarizeText = self.data

            return self.summarizeText 
