import json
import nltk
import os

#global variables
#sent_id = 1
triples_ignored = 0

#read the sent_id from a doc
sent_id_fp = open('sent_id.txt', 'r')
sent_id = int(sent_id_fp.readline().strip())
sent_id_fp.close()


#The following method takes a triple in the form of a string and returns it in triples form
def get_triple(triple_str : str):
    len_str = len(triple_str)
    if(triple_str[0]!='[' or triple_str[len_str-1]!=']'):
        #the string does not represent a valid triple
        return None
    
    #get rid of the '[' and ']'
    triple_str = triple_str[1:-1]
    
    triple = triple_str.split(',')
    if(len(triple)!=3):
        print("ERROR : Unable to split the following triple properly:\n" + triple_str + "\n")
        return None
    
    #get rid of leading or trailing white spaces and quotes(', ')
    triple[0] = triple[0].strip()[1:-1]
    triple[1] = triple[1].strip()[1:-1]
    triple[2] = triple[2].strip()[1:-1]
    
    return triple


def get_alternate_forms(word : str):
    word = word.lower()
    alt_words = []
    
    if(word=="gram"):
        alt_words = ['gram', 'gms', 'g', 'gm', 'grams']
    elif(word=="hour"):
        alt_words = ['hour', 'hr', 'h']
    elif(word=="milliampere"):
        alt_words = ['milliampere', 'ma', 'milliamps', "milliamperes"]
    elif(word=="percent"):
        alt_words = ["percent", "perc", "percentage", "%"]
    elif(word=="volt"):
        alt_words=["volt", "v", "volts", "vlt", "vlts"]
    elif(word=="kilogram"):
        alt_words=["kilogram", "kilograms", "kgs", "kg", "kilos"]
    elif(word=="watthour"):
        alt_words=["watthour", "watt", "wh", "w", "whr"]
    elif(word=="centimeter"):
        alt_words=['centimeter', 'cm', 'cms', 'centimeters']
    elif(word=="siemens"):
        alt_words = ['siemens', 'siemen', 's']
    elif(word=="ampere"):
        alt_words = ['ampere', 'amperes', 'amp', 'amps', 'a']
    else:
        alt_words = [word]
        
    return alt_words
    



def gen_relations_mentions_items(sent : str, triples : list, docId : int):
    relation_mentions = []
    
    sent = sent.strip()
    sent_l = sent.lower()
    
    words = nltk.word_tokenize(sent_l)
    
    #the following file will contain all the sentence, triple pairs that could not be parsed
    unparsed_fp = open('Pairs_not_parsed.txt', 'a')
    
    word_map = dict()
    # Example : word_map["king"] = [4, 9] => it means, "king" is present in positions 5th and 10th in "sent".
    for i,word in enumerate(words):
        if(len(word)>=3 and word[-2]=='-' and (word[-1]=='1' or word[-1]=='2' or word[-1]=='3')):
            word = word[:-2]
        
        if(word_map.get(word)==None):
            word_map[word] = [i]
        else:
            pos_list = word_map[word]
            pos_list.append(i)
            word_map[word] = pos_list
    
    #debug
    #print("\n\n\n")
    #print(word_map)
    
    for triple in triples:
        
        triple_l = [triple[i].strip().lower() for i in range(3)]
        item = dict()
        item['arg1Text'] = triple[0]
        
        #Search and update the start index of entity_1 i.e. triple[0]
        if(word_map.get(triple_l[0])!=None):
            #We use the first occurence of the entity
            item['arg1StartIndex'] = word_map[triple_l[0]][0]
        else:
            # entity1 in sent may have split into multiple words
            terms = nltk.word_tokenize(triple_l[0])
            
            if(word_map.get(terms[0])==None):
                #Unable to parse this sentence; Write the sentence, triple pair to a special file and ignore parsing it.
                #unparsed_fp.write(sent + "\n" + str(triple) + "\nEntity 1 :: Here" + "\n\n")
                unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                continue
            else:
                #list of indices where term0 appears in the sentence
                pos_term_0 = word_map[terms[0]]
                
                match_i = False
                for pos_t_0 in pos_term_0:
                    for i, term in enumerate(terms[1:]):
                        #flag that denotes term_i is present at correct position
                        match_i = False
                        
                        #list of indices where term_i appears in the sentence
                        if(word_map.get(term)==None):
                            match_i = False
                            break
                            
                        pos_term_i = word_map[term]
                        
                        for pos_t_i in pos_term_i:
                            if(pos_t_i== (pos_t_0 + i + 1)):
                                match_i = True
                                break
                        
                        if(match_i==False):
                            # term_i is not present at the required position; This pos_t_0 is not the correct 
                            #location of occurrence
                            break
                    
                    if(match_i==True):
                        #It means the inner loop was not "broken", which means pos_t_0 is the correct index where arg1 occurs
                        item['arg1StartIndex'] = pos_t_0
                        break
                
                if(match_i==False):
                    #It means entity_1 could not be parsed
                    unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                    #unparsed_fp.write(sent + "\n" + str(triple) + "\nEntity 1" + "\n\n")
                    continue #ignore this triple, and go to the next triple
        
        #Update the end index of entity_1 i.e., triple[0]
        item['arg1EndIndex'] = item['arg1StartIndex'] + len(triple_l[0].split(' ')) - 1
        
        
        #Search and Update the start and end indices of relation i.e. triple[1]
        item['relText'] = triple[1]
        if(word_map.get(triple_l[1])!=None):
            item['relStartIndex'] = word_map[triple_l[1]][0]
            item['relEndIndex'] = item['relStartIndex']
        else:
            #relation consists of multiple tokens
            terms = nltk.word_tokenize(triple_l[1])
            
            if(word_map.get(terms[0])==None):
                #Unable to parse this sentence; Write the sentence, triple pair to a special file and ignore parsing it.
                #unparsed_fp.write(sent + "\n" + str(triple) + "\nRelation" +"\n\n")
                unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                continue
            else:
                #the
                pos_term_0 = word_map[terms[0]]
                
                match_i = False
                for pos_t_0 in pos_term_0:
                    for i, term in enumerate(terms[1:]):
                        #flag that denotes term_i is present at correct position
                        match_i = False
                        
                        #list of indices where term_i appears in the sentence
                        if(word_map.get(term)==None):
                            match_i = False
                            break
                            
                        pos_term_i = word_map[term]
                        
                        for pos_t_i in pos_term_i:
                            if(pos_t_i== (pos_t_0 + i + 1)):
                                match_i = True
                                break
                        
                        if(match_i==False):
                            # term_i is not present at the required position; This pos_t_0 is not the correct 
                            #location of occurrence
                            break
                    
                    if(match_i==True):
                        #It means the inner loop was not "broken", which means pos_t_0 is the correct index where arg1 occurs
                        item['relStartIndex'] = pos_t_0
                        break
                
                if(match_i==False):
                    #It means entity_1 could not be parsed
                    unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                    #unparsed_fp.write(sent + "\n" + str(triple) + "\nRelation" + "\n\n")
                    continue #ignore this triple, and go to the next triple
                
                #item['relStartIndex'] = word_map[terms[0]][0]
            
            item['relEndIndex'] = item['relStartIndex'] + len(terms) - 1
        
        
        #Search and Update the start and end indices for entity_2 i.e. triple[2]
        item['arg2Text'] = "none" #just a place holder
        item['arg2OriginalText'] = triple[2]
        if(word_map.get(triple_l[2])!=None):
            item['arg2StartIndex'] = word_map[triple_l[2]][0]
        else:
            #the following needs to be done to get rid of the "^(1.0)" or "^(-1.0)" type of part in entity_2
            terms = triple_l[2].split(" ")
            terms_new = []
            for term in terms:
                index = term.find("^(")
                if(index!=-1):
                    term = term[:index]
                
                terms_new.append(term)
            
            triple_l[2] = " ".join(terms_new)

            # entity2 in sent may have got split into multiple words
            terms = nltk.word_tokenize(triple_l[2])

            #DEBUG
            '''
            print("entity 2 : ")
            print(terms)
            print("\n\n\n")
            '''
            e2_len = 2 #initializing to 2, so that the value of the previous iteration doesnt get used
            if(word_map.get(terms[0])==None):
                #Unable to parse this sentence; Write the sentence, triple pair to a special file and ignore parsing it.
                unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                #unparsed_fp.write(sent + "\n" + str(triple) + "\nEntity 2" + "\n\n")
                continue
            else:
                #all the positions of sentence where the numeric part of entity_2 is present
                pos_term_0 = word_map[terms[0]]
                
                e2_len = len(terms)
                match_i = False
                for pos_t_0 in pos_term_0:
                    for i,term in enumerate(terms[1:]):
                        #match_i maintains the status of whether term_i matches the required position or not
                        match_i = False

                        pos_term_i = []
                        
                        #each term must be present within e2_len distance of term_0
                        #pos_term_i will contain all the positions where term_i appears in the sentence
                        #We also need to check for the alternate terms like 'gm' or 'gms' for 'gram'.
                        alt_terms = get_alternate_forms(term)
                        #debug
                        '''
                        print('alter:')
                        print(alt_terms)
                        '''
                        for alt_term in alt_terms:
                            if(word_map.get(alt_term)!=None):
                                pos_term_i = word_map[alt_term]
                                break
                        
                        for pos_t_i in pos_term_i:
                            if((pos_t_i-pos_t_0) <= (e2_len-1)):
                                match_i = True
                                #debug
                                #print(pos_t_i)
                                break
                        
                        if(match_i==False):
                            # term_i is not present at the required position; This pos_t_0 is not the correct 
                            #location of occurrence
                            break
                    
                    
                    if(match_i==True):
                        #It means the inner loop was not "broken", which means pos_t_0 is the correct index where arg1 occurs
                        item['arg2StartIndex'] = pos_t_0
                        break
                
                if(match_i==False):
                    #It means entity_2 could not be parsed
                    unparsed_fp.write(str(triple) + "\n" + str(docId) + "\n" + sent +"\n\n")
                    #unparsed_fp.write(sent + "\n" + str(triple) + "\nEntity 2" + "\n\n")
                    continue #ignore this triple, and go to the next triple                    
                
        
        #Update the end index of entity_2 i.e., triple[2]
        item['arg2EndIndex'] = item['arg2StartIndex'] + e2_len - 1
        item['arg2Text'] = ' '.join(nltk.word_tokenize(sent)[item['arg2StartIndex'] : (item['arg2EndIndex']+1)])
        
        relation_mentions.append(item)
    
    unparsed_fp.close()
    
    return relation_mentions
        
        
#the following function returns a python3 dictionary object
#if (len_constrained) is made True, then only sentences shorter than min_len and longer than max_len are ignored
def generate_dictionary_obj(triples : list, sentence : str, doc_id : int, len_constrained : bool, min_len : int, max_len : int):
    global sent_id    
    global triples_ignored
    
    if(len_constrained==True):
        sentence_len = len(nltk.word_tokenize(sentence))
        if(sentence_len<min_len or sentence_len>max_len):
            return None
    
    dict_obj = dict()
    dict_obj['id'] = sent_id
    sent_id += 1
    
    dict_obj['docId'] = doc_id

    if("/" in sentence):
        sent = [] #temp
        words = nltk.word_tokenize(sentence)
        for word in words:
            if("/" in word):
                sub_wds = word.split("/")
                for i,sub_wd in enumerate(sub_wds):
                    if(i>0):
                        sent.append("/")
                    sent.append(sub_wd)
            else:
                sent.append(word)
        sentence = ' '.join(sent)
    
    #Reason of tokenizing and joining => "88.37%" would be changed to "88.37 %"
    dict_obj['sentText'] = ' '.join(nltk.word_tokenize(sentence))
    
    triplets = [] #this will contain the triples in triplet form, not as a sentence
    for triple_str in triples:
        #triple_str = triple_str.lower()
        triplet = get_triple(triple_str)
        if(triplet==None):
            triples_ignored += 1
            continue
        
        triplets.append(triplet)
    
    #generate relationMentions
    dict_obj['relationMentions'] = gen_relations_mentions_items(sentence, triplets, doc_id)
    
    return dict_obj

def generate_jsonl(input_filepath : str, len_constraint : bool, sent_min_len : int, sent_max_len : int):
    
    output_filepath = "Structured_dataset.jsonl"
    
    input_fp = open(input_filepath, 'r')
    output_fp = open(output_filepath, 'w')
    
    flag1 = False
    flag2 = False
    flag3 = False
    EOF_Reached = False
    
    prev_sent = ""
    triples = []

    num_sentences = 0
    cnt_pairs = 0
    cnt_pairs_sent = 0 #num of pairs generated over the sentence under consideration
    
    while(EOF_Reached==False):
        #Read the 3 next lines
        triple = input_fp.readline().strip()
        doc_id_str = input_fp.readline().strip()
        if(doc_id_str!=""):
            doc_id = int(doc_id_str)
            
        sent = input_fp.readline().strip()
        blank = input_fp.readline().strip()
        
        #Check if the End of File has been reached
        if(triple=="" and doc_id_str=="" and sent=="" and blank==""):
            #EOF reached
            EOF_Reached = True
            continue
        
        
        #Check if anything unusual has been read, an error
        if(triple=="" and sent!=""):
            print("ERROR :: Unexpected triple, sent pair!")
            print("Triple : " + str(triple))
            print("Sentence : " + str(sent))
            break
        
        if(sent==prev_sent):
            triples.append(triple)
            cnt_pairs_sent += 1
            #cnt_pairs += 1
        else:
            dict_obj = generate_dictionary_obj(triples, prev_sent, doc_id, len_constraint, sent_min_len, sent_max_len)
            if(dict_obj!=None):
                dict_obj['numTriples'] = cnt_pairs_sent
                json.dump(dict_obj, output_fp)
                num_sentences += 1
                output_fp.write("\n")
                cnt_pairs += cnt_pairs_sent
            
            prev_sent = sent
            triples = [triple]
            cnt_pairs_sent = 1
    
    
    if(triples!=[]):
        dict_obj = generate_dictionary_obj(triples, prev_sent, doc_id, len_constraint, sent_min_len, sent_max_len)
        if(dict_obj!=None):
            json.dump(dict_obj, output_fp)
            cnt_pairs += cnt_pairs_sent
        
    
    output_fp.close()
    input_fp.close()
    print("Structured dataset generated successfully!!")
    print("File name : " + str(input_filepath))
    print("Number of sentences : " + str(num_sentences))
    print("Number of pairs : " + str(cnt_pairs))


def preProcessFile(input_filepath : str, output_filepath : str):
    input_fp = open(input_filepath, "r")
    output_fp = open(output_filepath, "w")
    
    num_lines = 0

    while(True):
        line1 = input_fp.readline() #read the triple
        line2 = input_fp.readline() #read the doc_id
        line3 = input_fp.readline() #read the sentence
        line4 = input_fp.readline() #read the new line character put as a delimiter

        num_lines += 4

        if(line1=="" and line2=="" and line3=="" and line4==""):
            break

        while(line4!="\n"):
            line3 = line3.strip()
            line3 = line3 + " " + line4
            line4 = input_fp.readline()
            num_lines += 1
        
        output_fp.write(line1 + line2 + line3 + line4)
    
    print("File has been preprocessed successfully!")
    print("Number of lines written : " + str(num_lines))

    
def main():
    global triples_ignored    
    
    #input_file = "Elsevier_test.txt"
    #input_folder = "/home/samir-pg/Knowledge_Graph/Distant_Supervision/Temp_Workspace/Sentence_Triple_Pairs_upd"
    #input_folder = "/home/samir-pg/Knowledge_Graph/Distant_Supervision/Temp_Workspace/Sentence_Pairs_prep_upd"
    input_folder = "Unparsed"
    output_folder = "Preprocessed_Sentence_Triple_Pairs"

    #preprocess the input files
    for _,_,files in os.walk(input_folder):
        for f in files:
            preProcessFile(input_folder + "/" + f, output_folder + "/" + f)
            #generate_jsonl(output_folder + "/" + f, True, 10, 50)

    #generate structured dataset using the pre-processed files
    for _,_,files in os.walk(output_folder):
        for f in files:
            generate_jsonl(output_folder + "/" + f, True, 10, 50)

    print("Number of triples ignored : " + str(triples_ignored))

    #write the updated value of sent_id to 
    sent_id_fp = open('sent_id.txt', 'w')
    sent_id_fp.write(str(sent_id))
    sent_id_fp.close()

'''
def main():
    input_file = "/home/samir-pg/Knowledge_Graph/Distant_Supervision/Temp_Workspace/Sentence_Pairs_prep/Sentence_Triple_Pairs_From_Elsevier_2.txt_pp"
    #input_file = "Elsevier_test.txt"
    generate_jsonl(input_file, False, 10, 50)
'''
main()
