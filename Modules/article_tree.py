from transformers import pipeline
from transformers import SummarizationPipeline
from Modules.similarity import calculate_similarity
import re
import copy

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

    def calculate_count_of_words(self):
        self.root.calculate_count_of_words()

    def print_count_words(self):
        self.root.print_count_words("")
    
    def get_all_paragraph_nodes_as_list(self, threshold=7):
        self.calculate_count_of_words()
        return self.root.get_all_paragraph_nodes(threshold)
    
    def get_title_of_article(self):
        return self.root.data
    
    def summarize_parts(self, ratio, tokenizer, model, elasticityOfLength = 0.4):
        self.root.tokenize_node(tokenizer)
        self.calculate_count_of_words()
        
        allText = ""
        for child in self.root.children:
            allText += child.data + '\n' + child.summarize_article_with_ratio(ratio, tokenizer, model, elasticityOfLength, "") + '\n'

        return allText
    
    def summarize_parts_as_list(self, ratio, tokenizer, model, elasticityOfLength = 0.4):
        self.root.tokenize_node(tokenizer)
        self.calculate_count_of_words()

        parts = []
        for child in self.root.children:
            parts.append([child.data, child.summarize_article_with_ratio(ratio, tokenizer, model, elasticityOfLength, "")])

        return parts

    def merge_trees(self, otherTree, threshold=0.6, rootCheckedForThreshold=True):
        self.calculate_count_of_words()
        mergedTree = copy.deepcopy(self)
        if rootCheckedForThreshold:
            if get_similarity(self.root.get_text_from_node(7),otherTree.root.get_text_from_node(7)) < threshold:
                print("There is no similarity!! ", get_similarity(self.root.get_text_from_node(7),otherTree.root.get_text_from_node(7)))
                return mergedTree
        
        nodes = otherTree.get_all_paragraph_nodes_as_list()
        for node in nodes:
            print("new node")
            for child in mergedTree.root.children:
                print("new title")
                if child.put_text(node, threshold):
                    break
        
        return mergedTree                


class Node:
    def __init__(self, depth, id, data):
        self.depth = depth
        #id is None while the Node is external(Paragraph) node
        self.id = id 
        self.data = data.replace("-\r\n", "").replace("\r\n", " ").replace("-\n", "").replace("\n", " ")
        self.children = []
        self.countOfWords = 0
        self.countOfTokens = 0

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
            
    
    def get_text_from_node(self,threshold = 0):
        result = ""
        if self.id is None:
            if self.countOfWords > threshold:
                result= self.data
        else:
            for child in self.children:
                result += child.get_text_from_node(threshold)+" "

        return result

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

    def tokenize_node(self, tokenizer):
        totalCount = 0
        if self.id is not None:
            for child in self.children:
                totalCount += child.tokenize_node(tokenizer)

        else:
            tokenizedText = tokenize_text(self.data, tokenizer)
            totalCount = len(tokenizedText[0])

        self.countOfTokens = totalCount
        return totalCount 
    
    def print_count_tokens(self, path):
        print(path," ",self.countOfTokens)
        if self.countOfTokens < 7:
            print(self.data)
            
        for child in self.children:
            child.print_count_words(path+".")

    def get_all_paragraph_nodes(self, threshold=7):
        paragraphs = []

        if self.id is None:
            text = self.get_text_from_node(threshold)
            if "" != text:
                paragraphs.append(self)
        else:
            for child in self.children:
                paragraphs.extend(child.get_all_paragraph_nodes(threshold))

        return paragraphs
    
    def put_text(self, node, threshold):
        if(self.id is None):
            return False
        
        maxScore = 0
        maxindex = 0
        maxtext = ""
        text2 = node.get_text_from_node(7)
        print("new depth")
        #print("text1:\n",self.get_text_from_node(7),"\n","text2:\n",text2,"\n")
        for i in range(len(self.children)):
            text1 = self.children[i].get_text_from_node(7)
            score = get_similarity(text1,text2)
            if maxScore < score:
                maxindex = i
                maxScore = score
                maxtext = text1
        
        print("maxScore:", maxScore, maxindex)
        if(maxScore > threshold):
            print("INFO: A node inserted.")
            print("text1:\n",maxtext)
            print("text2:\n",text2)
            self.children.insert(maxindex + 1, node)
            return True
        
        elif(maxScore > 0.3):
            return self.children[i].put_text(node, threshold)
        
        return False
        
    def summarize_article_with_ratio(self, ratio, tokenizer, model, elasticityOfLength, id_path):
        print("SummarizeR",self.depth," ",id_path + self.id)
        result = ""
        if self.id is not None:
            if self.countOfTokens < 1024:
                text = self.get_text_from_node(7)
                cWord = count_words(text)
                inputs = tokenize_text(text,tokenizer)
                if len(inputs[0]) > 2:
                    summary_ids = summarize_tokens(inputs, int(ratio*cWord), model, elasticityOfLength)
                    result += detokenize_text(summary_ids, tokenizer) + '\n'
                else:
                    print("empty text tokenized!1")
                return result

            else:
                allText = ""
                totalCountOfTokens = 0
                for child in self.children:
                    if totalCountOfTokens + child.countOfTokens > 1024 and totalCountOfTokens != 0:
                        print("What we think that we send token", totalCountOfTokens)
                        cWord = count_words(allText)
                        inputs = tokenize_text(allText, tokenizer)

                        if len(inputs[0]) > 2:
                            summary_ids = summarize_tokens(inputs, int(ratio*cWord), model, elasticityOfLength)
                            result += detokenize_text(summary_ids, tokenizer) + '\n'
                        else:
                            print("empty text tokenized!2")

                        allText = ""
                        totalCountOfTokens = 0
                    
                    if child.countOfTokens >= 1024:
                        result += child.summarize_article_with_ratio(ratio, tokenizer, model, elasticityOfLength,  id_path + str(self.id) +".")
                    
                    else:
                        allText += child.get_text_from_node(7)
                        totalCountOfTokens += child.countOfTokens

                if totalCountOfTokens <1024 and totalCountOfTokens != 0:
                        print("What we think that we send token", totalCountOfTokens)
                        cWord = count_words(allText)
                        inputs = tokenize_text(allText, tokenizer)
                        if len(inputs[0]) > 2:
                            summary_ids = summarize_tokens(inputs, int(ratio*cWord), model, elasticityOfLength)
                            result += detokenize_text(summary_ids, tokenizer) + '\n'
                        else:
                            print("empty text tokenized!3")

                return result
            
            
        else:
            if self.countOfTokens < 1024:
                print("What we think that we send token", totalCountOfTokens)
                cWord = count_words(self.data)

                inputs = tokenize_text(self.data, tokenizer)
                if len(inputs[0]) > 2:
                    summary_ids = summarize_tokens(inputs, int(ratio*cWord), model, elasticityOfLength)
                    result += detokenize_text(summary_ids, tokenizer) + '\n'
                else:
                    print("empty text tokenized!4")

                return result
            
            else:
                strings = []
                if self.countOfTokens < 2000:
                    strings = divide_to_strings(self.data, int(self.countOfTokens / 2))
                else:
                    strings = divide_to_strings(self.data, 1000)

                for text in strings:
                    cWord = count_words(text)
                    inputs = tokenize_text(text, tokenizer)

                    if len(inputs[0]) > 2:
                        summary_ids = summarize_tokens(inputs, int(ratio*cWord), model, elasticityOfLength)
                        result += detokenize_text(summary_ids, tokenizer) + ' '

                return result


def divide_to_strings(string, size):
    words = string.split()
    groups = []
    for i in range(0, len(words), size):
        group = ' '.join(words[i:i+size])
        groups.append(group)
    return groups            

def summarize_tokens(inputs, summarize_length, model, elasticityOfLength):
    summary_ids = None
    try:
        #re.sub(r'\n+', r'\n', text)
        #result = model(text, max_length=summarize_length, min_length=int(summarize_length*(1 - elasticityOfLength)), do_sample=False)[0]['summary_text']
        summary_ids = model.generate(inputs["input_ids"], num_beams=2, min_length=int(summarize_length*(1 - elasticityOfLength)), max_length=summarize_length)
    except Exception as e:
        print("!Error occurred while summarizing tokens:", e)
        print(inputs,"\n")
    return summary_ids

def tokenize_text(text, tokenizer):
    inputs = None
    try:
        #re.sub(r'\n+', r'\n', text)
        inputs = tokenizer([text], max_length=1024, truncation=True, return_tensors="pt")
    except Exception as e:
        print("!Error occurred while tokenize:", e)
        print(text,"\n")
    return inputs

def detokenize_text(summary_ids, tokenizer):
    result = None
    try:
        #re.sub(r'\n+', r'\n', text)
        result = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    except Exception as e:
        print("!Error occurred while detokenize:", e)
        print(summary_ids,"\n")
    return result

def get_similarity(text1, text2):
    score = 0
    try:
        score = calculate_similarity([text1,text2])
    except Exception as e:
        print("!Error occurred while calculating similarity:", e)
        print("text1 ::",text1,"\n","text2 ::",text2,"\n")
    return score
    