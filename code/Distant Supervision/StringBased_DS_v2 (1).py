import json
import nltk
import pickle
import os
import re


#gloabal variable 
triples_map = dict()
#pickled_map_file = open('Distant_Supervision/ent1_triple_map', 'rb')
pickled_map_file = open('Distant_Supervision/unique_triples_map', 'rb')

#reading the reduced map
#pickled_map_file = open('reduced_triple_map', 'rb')
triples_map = pickle.load(pickled_map_file)
pickled_map_file.close()
print('Triples Map loaded successfully!', flush=True)


pickled_regex_map_file = open('regex_map.pkl', 'rb')
regex_map = pickle.load(pickled_regex_map_file)
pickled_regex_map_file.close()
print('Regex map loaded successfully!', flush=True)


#global variable unique doc id
unq_doc_id = 0
'''
doc_id_fp = open('Unique_doc_id_seed.txt', 'r')
line = doc_id_fp.readline().strip()
unq_doc_id = int(line)
doc_id_fp.close()
'''

#start : global variables to maintain stats about the corpus
sent_longer_200 = 0 #num of sentences longer than 200
sent_longer_100 = 0 #num of sentences longer than 100 but shorter than 200
sent_longer_50 = 0
sent_total = 0 #total number of sentences

print('Global variables initialized')

#end



def get_sentence_triple_pairs(sent : str, triples : list):
    pos_tri = []
    
    sent = sent.lower()
    
    for triple in triples:
        #split the entity_2 of the triple into words
        e3_words = triple[2].split(' ')
        
        for word in e3_words:
            word = word.lower()
            #Change, "gram^(1.0)" to "gram"
            if('^' in word):
                index = word.find('^(')
                word = word[:index]
            
            #if the word is present in the triple, we consider the triple as positive
            if(word in sent):
                pos_tri.append(triple)
                break
    
    print('Total number of (sentence, triple) pairs identified : ' + str(len(pos_tri)), flush=True)
    
    return pos_tri


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
    

#the following function returns a list of all the triples that have 'entity 2' in the passed sentence
def get_sentence_triple_pairs_Stricter(sent : str, triples : list, strictness : float):
    pos_tri = []
    
    sent = sent.lower()
    
    #strictness = 0.8
    
    for triple in triples:
        #split the entity_2 of the triple into words
        e3_words = triple[2].split(' ')
        e3_words = [w for w in e3_words if(w!="")] #sometimes, "" was appearing as a word, this line filters such words
        
        #contains the number of words in the entity2 part of the triple
        counter = 0
        
        for word in e3_words:
            word = word.lower()
            
            #check if the word is completely numberic, like "234.8" for instance.
            temp = word.replace('.', '8').replace('-', '')
            if(temp.isnumeric()):
                counter += 1
                continue
                
            
            #Change, "gram^(1.0)" to "gram"
            if('^' in word):
                index = word.find('^(')
                word = word[:index]
            
            #get alternate forms like, 'gm' for 'grams'
            alt_forms_word = get_alternate_forms(word)
            
            #if the word is present in the triple, we consider the triple as positive
            words_in_sentence = nltk.word_tokenize(sent)
            for wd in alt_forms_word:
                if(wd in words_in_sentence):
                    counter += 1
                    break
        
        
        if((counter/len(e3_words))>=strictness):
            pos_tri.append(triple)
    
    #print('Total number of (sentence, triple) pairs identified : ' + str(len(pos_tri)))
    
    return pos_tri
    


#The following function returns a list of all the triples that have 'entity 2' in the passed sentence. 
#This newer version is based on very strict matching as instructed by Sir.
def get_sentence_triple_pairs_Stricter_V2(sent : str, triples : list, strictness : float):
    pos_tri = []
    
    sent = sent.lower()
    
    words_in_sentence = nltk.word_tokenize(sent)
    
    #minor optimization : ignore the sentence if it is longer than 50 words
    '''
    if(len(words_in_sentence)>45):
        return pos_tri
    '''
    #construct a hash table with [word, (list of positions of "word" in sent)]
    #For example, sent : "king of the king." => words_in_sent_map["king"] = [0, 3]
    words_in_sent_map = dict()
    for i, word in enumerate(words_in_sentence):
        #if word='gram-1', then make word='gram'
        if((len(word)>2) and (word[-2]=='-') and (word[-1]=='1' or word[-1]=='2' or word[-1]=='3')):
            word = word[:-2]
        
        if(words_in_sent_map.get(word)==None):
            #if the "word" doesn't exist in the map, then we store a list with only the word's present index as value 
            words_in_sent_map[word] = [i]
        else:
            #word already exists in the map, then we add index 'i' to the existing list in the map 
            #minor optimization
            '''
            index_list = words_in_sent_map[word]
            index_list.append(i)
            words_in_sent_map[word] = index_list
            '''
            words_in_sent_map[word].append(i)
    #strictness = 0.8
    #prev_index = 0
    #print(words_in_sent_map)
    
    for triple in triples:
        #split the entity_2 of the triple into words
        e3_words = triple[2].split(' ')
        e3_words = [w for w in e3_words if(w!="")] #sometimes, "" was appearing as a word, this line filters such words
        
        #DEBUG
        #print(e3_words)
        
        #contains the number of words in the entity2 part of the triple
        counter = 0
        word_pos = [] #this will contain lists of positions in sentence where each word in e3_words occurs
        numeric_value_found = False #determines if the numeric part of the entity_2 is present in the given sentence
        for word in e3_words:
            
            #check if the word is completely numberic, like "234.8" for instance.
            temp = word.replace('.', '8').replace('-', '')
            if(temp.isnumeric()):
                if(words_in_sent_map.get(word)!=None):
                    word_pos.append(words_in_sent_map[word])
                    #DEBUG
                    #print(word_pos)
                    continue
                else:
                    #numeric value not found in the sentence, hence go to the next triple
                    break
                '''
                for i, wd in enumerate(words_in_sentence):
                    if(wd==word):
                        counter += 1
                        prev_index = i
                        numeric_value_found = True
                        break
                #counter += 1
                if(numeric_value_found == True):
                    continue
                else:
                    #numeric value not found in the sentence, hence go to the next triple
                    break
                '''
            
            #Change, "gram^(1.0)" to "gram"
            if('^' in word):
                index = word.find('^(')
                word = word[:index]
            
            #get alternate forms like, 'gm' for 'grams'
            alt_forms_word = get_alternate_forms(word)
            
            #if the word is present in the triple, we consider the triple as positive
            temp_list = []
            for wd in alt_forms_word:
                if(words_in_sent_map.get(wd)!=None):
                    temp_list.extend(words_in_sent_map[wd])
            
            #DEBUG
            #print(temp_list)
            
            if(not temp_list):
                #temp_list is empty, it means this "word" is not present in the "sent"
                word_pos = []
                break
            else:
                word_pos.append(temp_list)
            
            #DEBUG
            #print(word_pos)
            
            '''
            for wd in alt_forms_word:
                if(wd in words_in_sentence):
                    counter += 1
                    break
            '''
            
        '''
        if((counter/len(e3_words))>=strictness):
            pos_tri.append(triple)
        '''
        
        if(not word_pos):
            #word_pos is empty
            continue
        
        if(isValidSequence_V2(word_pos)==True):
            pos_tri.append(triple)
    #print('Total number of (sentence, triple) pairs identified : ' + str(len(pos_tri)))
    
    return pos_tri


#the following function accepts a list of lists as input, and returns a boolean value
def isValidSequence(word_pos_list : list):
    #print(word_pos_list)
    #Example sequence : [[3, 12], [4, 16, 22], [5, 9], [6]] is valid because 
    #                   [   3,      4,           5,     6 ] make a continuous monotonically increasing sequence
    #Example of invalid sequence : [[3, 12], [7, 14], [4, 16, 22], [5, 9], [6]]
    #                                         This  7 breaks the monotonically increasing sequence   
    if(not word_pos_list):
        # if word_pos is empty
        return False
    
    pos_list_0 = word_pos_list[0]
    pos_list_len = len(word_pos_list)
    for pos in pos_list_0:
        valid = True
        for i in range(pos_list_len-1):
            if((pos + i + 1) not in word_pos_list[i+1]):
                valid = False
                break
    #for pos_list in word_pos[1:]:
        if(valid==True):
            break
            
    return valid
    

#the following function accepts a list of lists as input, and returns a boolean value
def isValidSequence_V2(word_pos_list : list):
    #print(word_pos_list)
    #Example sequence : [[4, 12], [3, 16, 22], [5, 9], [6]] is valid because
    #                   [   4,      3,           5,     6 ] make a continuous monotonically increasing sequence when sorted
    #Example of invalid sequence : [[3, 12], [7, 14], [4, 16, 22], [5, 9], [6]]
    #                                         This  7 breaks the monotonically increasing sequence
    if(not word_pos_list):
        # if word_pos is empty
        return False

    #pos_list_0 = word_pos_list[0]
    pos_list_len = len(word_pos_list)

    max_index = 0
    for indices in word_pos_list:
        for index in indices:
            if(index>max_index):
                max_index = index
    #max_index now roughly denotes the number of words present in the underlying sentence


    #Create a list with elements = the number of words in the sentence, wherein each element is 0 initially
    seq_list = []
    for i in range(max_index+1):
        seq_list.append(0)

    #make all the index positions in the 'word_pos_list' as 1.
    for indices in word_pos_list:
        for index in indices:
            seq_list[index] = 1

    #Now search for a continuous run of 1s of length 'pos_list_len' in seq_list
    valid = False #this flag would contain the return value of the function
    for i in range(max_index):
        if(seq_list[i]==1):
            valid = True
            for j in range(pos_list_len):
                #monitor for list index going out of bounds
                if(i+j>max_index):
                    valid = False
                    break
                elif(seq_list[i+j]==0):
                    valid = False
                    break

            if(valid==True):
                #Valid sequence found
                break

    return valid




#the following function returns a list of all triples with entity_1 present in the passed sentence 
def get_triples_wrt_e1(sent : str):
    positive_triples = []
    
    words = nltk.word_tokenize(sent)
    for word in words:
        if(triples_map.get(word)==None):
            continue
        
        #word is present in the triples as entity 1
        positive_triples += triples_map[word]
    
    
    return positive_triples

def genRegexExpression(in_str : str):
    pattern = ""
    special_symbols = ['.', '+', '*', '\\','^', '$','|', '?','{', '}','[', ']','(', ')']
    
    for i in range(len(in_str)):
        if(in_str[i] in special_symbols):
            pattern += "\\"
            
        pattern += in_str[i]
    
    return pattern

#generate and store the regex patterns corresponding to the each entity_1 part of all triples
def generate_regex_map_for_triples():
    positive_triples = []
    
    #the following map would contain items : "entity_1 : regex_pattern_of_entity1"
    regex_map = dict()
    
    #words = nltk.word_tokenize(sent)
    for entity_1 in triples_map.keys():
        entity_1_regex = genRegexExpression(entity_1)
        regex_map[entity_1] = entity_1_regex
    
    #store the regex_map in a pickle file
    pickle_file = open('regex_map.pkl', 'wb')
    pickle.dump(regex_map, pickle_file)
    pickle_file.close()
    
    print('Regex map pickled successfully!')


#the following function returns a list of all triples with entity_1 present in the passed sentence 
def get_triples_wrt_e1_V2(sent : str):
    positive_triples = []
    
    #words = nltk.word_tokenize(sent)
    for entity_1 in triples_map.keys():
        #modification: start
        #entity_1_regex = genRegexExpression(entity_1)
        #another optimization
        if(regex_map.get(entity_1)==None):
            continue
        
        entity_1_regex = regex_map[entity_1]
        pattern = '\W' + entity_1_regex + '\W' #\W matches any non-alphanumeric character, equivalent to [^0-9a-zA-Z_]
        #if(entity_1 in sent):
        #print(pattern)
        if(re.search(pattern, sent)!=None):
            positive_triples += triples_map[entity_1]
        
        #word is present in the triples as entity 1
        #positive_triples += triples_map[word]

    #print('Done...', flush=True)
    
    
    return positive_triples


#the following function returns a list of all triples with entity_1 present in the passed sentence 
def get_triples_wrt_e1_V3(sent : str):
    positive_triples = []
    
    #sent = sent.lower()
    words = nltk.word_tokenize(sent)
    
    #start : update stats
    '''
    global sent_total
    global sent_longer_200
    global sent_longer_100
    global sent_longer_50

    sent_total += 1
    
    if(len(words)>200):
        sent_longer_200 += 1
    elif(len(words)>100):
        sent_longer_100 += 1
    elif(len(words)>50):
        sent_longer_50 += 1
    '''
    #end : update stats

    #search the triples_map for each word in the sentence
    for word in words:
        if(triples_map.get(word)!=None):
            positive_triples += triples_map[word]
        #if the word contains any of "/" or "*" or "\", then split the word using these, and search the triples_map for the resulting sub_words
        elif("/" in word):
            sub_words = word.split("/")
            for s_word in sub_words:
                if(triples_map.get(s_word)!= None):
                    positive_triples += triples_map[s_word]
        elif("*" in word):
            sub_words = word.split("*")
            for s_word in sub_words:
                if(triples_map.get(s_word)!= None):
                    positive_triples += triples_map[s_word]
        elif("\\" in word):
            sub_words = word.split("\\")
            for s_word in sub_words:
                if(triples_map.get(s_word)!= None):
                    positive_triples += triples_map[s_word]
    
    return positive_triples


#the following function returns a list of (triple, sentence) pairs corresponding to the "doc_path"
#doc_id => unique id for each document. It starts from 1.
def get_sentence_triples_pairs_in_a_doc(doc_path : str, strictness : float):
    global unq_doc_id
    
    unq_doc_id += 1 #increment the doc_id
    doc_fp = open(doc_path, 'r')
    line = doc_fp.read()
    line = line.strip()
    
    json_item = json.loads(line)
    
    #doc_text will contain all the text in the paper
    doc_text = json_item["metadata"]["abstractText"]
    if(doc_text==None):
        doc_text=""
    
    sections = json_item["metadata"]["sections"]
    
    #Because NoneType object is not iterable
    if(sections==None):
        sections = []
        
    for section in sections:
        doc_text += ' \n'
        if(section['text']!=None):
            doc_text += section["text"]
    
    
    #divide the doc_text into sentences
    sentences = nltk.sent_tokenize(doc_text)
    sent_triple_pairs = []
    
    #Because NoneType object is not iterable
    if(sentences==None):
        sentences = []
    
    for sentence in sentences:
        positive_triples = get_triples_wrt_e1_V3(sentence)
        
        #filter out positive_triples with respect to the presence of entity_2 part in the sentence.
        #positive_triples = get_sentence_triple_pairs_Stricter(sentence, positive_triples, strictness)
        positive_triples = get_sentence_triple_pairs_Stricter_V2(sentence, positive_triples, strictness)
        
        #filter out triples based on the presence of relation part in the sentence
        positive_triples = get_triples_wrt_relation(sentence, positive_triples)

        #this is where you should place the stats, after chekcing if positive_triples is not empty
        if((positive_triples != None) and (positive_triples!=[])):
            #update stats
            global sent_total
            global sent_longer_200
            global sent_longer_100
            global sent_longer_50

            sent_total += 1
            words = nltk.word_tokenize(sentence)

            if(len(words)>200):
                sent_longer_200 += 1
            elif(len(words)>100):
                sent_longer_100 += 1
            elif(len(words)>50):
                sent_longer_50 += 1

        for triple in positive_triples:
            sent_triple_pairs.append([triple, unq_doc_id, sentence])
    
    print("Number of pairs identified : " + str(len(sent_triple_pairs)), flush=True)
    return sent_triple_pairs


#The following method accepts a list of triples and a sentence as input and returns the triples that have their relation 
#part present in the sentence.
def get_triples_wrt_relation(sent : str, triples : list):
    
    positive_triples = []
    sent = sent.lower()
    
    for triple in triples:
        pattern = '\W' + genRegexExpression(triple[1].lower()) + '\W' #\W matches any non-alphanumeric pattern
        if(re.search(pattern, sent)!=None):
            positive_triples.append(triple)
    
    return positive_triples



def get_pairs_for_all_docs(folder_path : str, strictness : float, output_filepath : str):
    sent_triple_pairs = []
    cnt = 0 #holds the number of docs read so far
    num_pairs_generated = 0
    
    for (root, dirs, files) in os.walk(folder_path, topdown=True):
        for f in files:
            sent_triple_pairs += get_sentence_triples_pairs_in_a_doc(root + '/' + f, strictness)
            cnt += 1
            if(cnt%50==0):
                pairs_fp = open(output_filepath, 'a')
                num_pairs_generated += len(sent_triple_pairs)
                for pair in sent_triple_pairs:
                    pairs_fp.write(str(pair[0]) + '\n' + str(pair[1]) + '\n' + pair[2] + '\n\n')

                pairs_fp.close()
                sent_triple_pairs = []
                print('Number of files scanned so far : ' + str(cnt), flush=True)

                #DEBUG
                #print("DEBUG :: Breaking it here!!")
                #break
        
    
    num_pairs_generated += len(sent_triple_pairs)
    pairs_fp = open(output_filepath, 'a')
    for pair in sent_triple_pairs:
        pairs_fp.write(str(pair[0]) + '\n' + str(pair[1]) + '\n' + pair[2] + '\n\n')

    pairs_fp.close()
    print('Number of (sentence, triple) pairs generated on the entire corpus : ' + str(num_pairs_generated))
    return sent_triple_pairs

#The following function will generate multiple files each containing names of 1000 json files
# file 'json_file_names_<i>' would serve as a target file for thread <i>  
#Multi-thread
#input : folder_path => path to the folder containing all the json files
#This function returns the number of chunk files created.
def generateTargetFilesForMultiThreads(folder_path : str, output_folder : str):
    cnt = 0
    index = 1
    target_filename = output_folder + "/chunk_"
    
    fp = open(target_filename + str(index) + '.txt', 'w')
    for (root, dirs, files) in os.walk(folder_path):
        for f in files:
            fp.write(root + '/' + f + '\n')
            cnt += 1
            
            if(cnt%1000==0):
                fp.close()
                index += 1
                fp = open(target_filename + str(index) + '.txt', 'w')
    
    fp.close()
    
    #return the count of chunk files generated
    return index


#Multi-threaded
#input : chunk_file_folder_path => path to the folder containing all the "chunk" files
#        chunk_index => like thread-index
def generate_pairs_from_one_chunk_of_files(chunk_file_folder_path : str, chunk_index : int, output_folder : str):
    chunk_filename = chunk_file_folder_path + "/" + "chunk_" + str(chunk_index) + ".txt"
    output_filename = output_folder + '/' + 'pairs_' + str(chunk_index) + '.txt'
    
    chunk_fp = open(chunk_filename, 'r')
    
    cnt = 0
    sent_triple_pairs = []
    for line in chunk_fp.readlines():
        line = line.strip()
        sent_triple_pairs += get_sentence_triples_pairs_in_a_doc(line, 1.0)
        cnt += 1
        
        if(cnt%50==0):
            #write the pairs to output file
            out_fp = open(output_filename, 'a')
            for pair in sent_triple_pairs:
                out_fp.write(pair[0] + '\n' + pair[1] + '\n\n')
            out_fp.close()
            sent_triple_pairs = []
            print('Thread_' + str(chunk_index) + ':: files read so far :' + str(cnt), flush=True)
    
    out_fp = open(output_filename, 'a')
    for pair in sent_triple_pairs:
        out_fp.write(pair[0] + '\n' + pair[1] + '\n\n')
    out_fp.close()
    
    

def main_for_mutithreaded():
    #path containing all the json files
    doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/output"
    
    #folder that would contain all the chunk files
    folder_chunk_files = "/home/samir-pg/Knowledge_Graph/Distant_Supervision/chunk_files/"
    
    #folder that would contain all the (triple, sentence) pairs
    folder_pairs = "/home/samir-pg/Knowledge_Graph/Distant_Supervision/Sent_Triple_Pairs"
    
    #generate the chunk files
    num_threads = generateTargetFilesForMultiThreads(doc_path, folder_chunk_files)
    
    #list containing references to all the threads created
    all_threads = []
    
    #generate the threads
    for i in range(num_threads):
        t = threading.Thread(target=generate_pairs_from_one_chunk_of_files, args=(folder_chunk_files, i, folder_pairs,))
        t.start()
        all_threads.append(t)
    
    
    #wait until all threads complete execution
    for t in all_threads:
        t.join()
        
    print('Execution Complete!')


def main():
    '''
    sent = "Capacity of carbon is measured in some gram and hour and MilliAmpere"
    triples = [['Zn2SnO4 anodes', 'Capacity', '-448.0 Gram^(-1.0)  Hour^(1.0)  MilliAmpere^(1.0)'], 
               ['Carbon', 'Capacity', '242.9 Gram^(-1.0)  Hour^(1.0)  MilliAmpere^(1.0)'], 
               ['TiO2 electrodes', 'Voltage', '3.0 Volt^(1.0)']]
    
    pos_tri = get_sentence_triple_pairs_Stricter(sent, triples, 1.0)
    '''
    
    #read the doc_id
    global unq_doc_id
    
    doc_id_fp = open('Unique_doc_id_seed.txt', 'r')
    line = doc_id_fp.readline().strip()
    unq_doc_id = int(line)
    doc_id_fp.close()
    
    #doc_path = "/home/samir-pg/Knowledge_Graph/all_jsons/29-01-2020-part2-1809.06076v1.Infrared_spectroscopic_studies_of_the_topological_properties_in_CaMnSb2.pdf.json"
    #29-01-2020-part2-1809.07810v1.Control_of_hidden_ground_state_order_in_NdNiO__3_superlattices.pdf.json"
    #29-01-2020-part2-1902.10916v1.First_principles_study_fabrication_and_characterization_of_Zr0_25Nb0_25Ti0_25V0_25_C_high_entropy_ceramic.pdf.json"
    #29-01-2020-part2-1906.06075v1.Route_to_Achieving_Enhanced_Quantum_Capacitance_in_Functionalized_Graphene_based_Supercapacitor_Electrodes.pdf.json"
    #29-01-2020-part2-1908.05585v1.Defect_Physics_of_Pseudo_cubic_Mixed_Halide_Lead_Perovskites_from_First_Principles.pdf.json"
    #sent_triple_pairs = get_sentence_triples_pairs_in_a_doc(doc_path, 0.6)
    
    #doc_path = "/home/samir-pg/Knowledge_Graph/ns_jsons"
    #doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/arxiv_500_json"
    
    
    #doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/arxiv_2930_json"
    #doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/Elsevier_Docs_1st_3k_json"
    #doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/Elsevier_Docs_json_2"
    #doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/Elsevier_Docs_json_3"
    doc_path = "/home/samir-pg/Knowledge_Graph/Science_Parse/science-parse-master/cli/Elsevier_Docs_json_5"
    #output_filepath = "Sentence_Triple_Pairs_From_Elsevier_1st_3k_rel.txt"
    output_filepath= "Sentence_Triple_Pairs_From_Elsevier_upd_5.txt"
    sent_triple_pairs = get_pairs_for_all_docs(doc_path, 0.7, output_filepath)
   
    #write the stats to a file 
    stats_fp = open('Corpus_stats.txt', 'w')
    stats_fp.write('Number of sentences longer than 200                      : ' + str(sent_longer_200) + '\n')
    stats_fp.write('Number of sentences longer than 100 but shorter than 200 : ' + str(sent_longer_100) + '\n')
    stats_fp.write('Number of sentences longer than 50 but shorter than 100  : ' + str(sent_longer_50) + '\n')
    stats_fp.write('Total Number of sentences                                : ' + str(sent_total) + '\n')
    stats_fp.close()
    
    #write the updated doc_id to the file
    doc_id_fp = open('Unique_doc_id_seed.txt', 'w')
    doc_id_fp.write(str(unq_doc_id))
    doc_id_fp.close()
    
    #pairs_fp = open('Sentence_Triple_Pairs.txt', 'w')
    #pairs_fp = open('Sentence_Triple_Pairs_From_Arxiv.txt', 'w')
    #pairs_fp = open('Sentence_Triple_Pairs_From_Arxiv_2930.txt', 'w')
    #pairs_fp = open('Sentence_Triple_Pairs_From_Elsevier_1st_3k.txt', 'w')

    '''
    for pair in sent_triple_pairs:
        pairs_fp.write(str(pair[0]) + "\n" + pair[1] + "\n\n")
    
    pairs_fp.close()
    '''
    #print('Positive triples : ')
    #print(pos_tri)
    #print("List of identified pairs:")
    #print(sent_triple_pairs)
    
    #print("Total number of pairs identified : " + str(len(sent_triple_pairs)))
    
    #seq = [[3, 12], [4, 16, 22], [5, 9], [6]]
    #seq = [[3, 12], [4, 14], [ 16, 22], [5, 9], [6]]
    #print("Result is : " + str(isValidSequence(seq)))
    
    '''
    sent = "The measured power or Capacity was 100 Wh."
    triples = [ ['power', 'capacity', '100 WattHour^(1.0)'], ['Current', 'Voltage', '100 Volts']]
    '''
    #pos_triples = get_sentence_triple_pairs_Stricter_V2(sent, triples, 1.0)
    #pos_triples = get_triples_wrt_relation(sent, triples)
    #print(pos_triples)
    

    '''
    sent1 = "INTRODUCTION Olivine-type FePO4 is a promising candidate and 143.65 Wh Kg-1 for rechargeable Li-ion battery electrodes.1 The material is known for its structural and chemical stabilities, high intercalation voltage (∼3.5 V relative to lithium metal), high theoretical discharge capacity (170 mAh/g), environmental friendliness, and potentially low costs.2,3 The major drawback of FePO4 is poor ionic and electronic conduction (with an electrical conductivity of about 10−9 S/cm at 298 K)4 that limits its applicability to devices."

    sent2 = "When ∆Gt is tuned to zero by adjusting the net surface electronic density, LiC6 is at the onset of deltihiation – experimentally known to occur at 0.1 V vs. Li+/Li(s)."

    sent3 = "Instead, when both Li(s) and LiC6 are at their respective ∆Gt=0.0 eV, EF in the two electrodes differs by 0.10 V according to experiments, and Eq."
    
    #pos_triples = get_triples_wrt_relation(sent1, triples)
    pos_triples = get_triples_wrt_relation(sent2, triples)
    pos_triples += get_triples_wrt_relation(sent3, triples)
    print(pos_triples)
    '''

    '''
    triples = get_triples_wrt_e1_V2(sent1)
    triples = get_sentence_triple_pairs_Stricter_V2(sent1, triples, 1.0)

    for triple in triples:
        print(triple)
    '''
main()
