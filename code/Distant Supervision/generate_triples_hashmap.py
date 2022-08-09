import pickle
import csv


def remove_duplicate_triples(pickled_map_filepath : str):
    
    pickled_map_file = open(pickled_map_filepath, 'rb')
    triples_map = pickle.load(pickled_map_file)
    pickled_map_file.close()
    print('Triples Map loaded successfully!')
    
    reduced_map = dict()
    for e1 in triples_map.keys():
        triples = triples_map[e1]
        
        relation_map = dict()
        for triple in triples:
            if(relation_map.get(triple[1])==None):
                #this relation doesn't exist
                relation_map[triple[1]] = triple
        
        unique_triples = []
        for rel in relation_map.keys():
            unique_triples.append(relation_map[rel])
        
        
        reduced_map[e1] = unique_triples
    
    #write the reduced_map to a pickle file
    pickle_file = open('reduced_triple_map', 'wb')
    pickle.dump(reduced_map, pickle_file)
    pickle_file.close()
    
    print("Reduced map pickled successfully!") 
                
    

def remove_duplicate_triples_V2(pickled_map_filepath : str):
    
    pickled_map_file = open(pickled_map_filepath, 'rb')
    triples_map = pickle.load(pickled_map_file)
    pickled_map_file.close()
    print('Triples Map loaded successfully!')
    
    reduced_map = dict()
    for e1 in triples_map.keys():
        triples = triples_map[e1]
        
        e2_map = dict()
        for triple in triples:
            if(e2_map.get(triple[2])==None):
                #this entity_2 value doesn't exist
                e2_map[triple[2]] = triple
        
        unique_triples = []
        for e2 in e2_map.keys():
            unique_triples.append(e2_map[e2])
        
        
        reduced_map[e1] = unique_triples
    
    #write the reduced_map to a pickle file
    pickle_file = open('unique_triples_map', 'wb')
    pickle.dump(reduced_map, pickle_file)
    pickle_file.close()
    
    print("Map with unique triples pickled successfully!") 
                




def gen_ent_triple_hashmap(triples_filepath : str):
    
    triples_fp = open(triples_filepath, 'r')
    tsv_reader = csv.reader(triples_fp, delimiter='\t')
    
    ent1_triple_map = dict()
    
    for row in tsv_reader:
        e1 = row[0].strip()
        if(ent1_triple_map.get(e1)==None):
            ent1_triple_map[e1] = [row]
        else:
            triples_list = ent1_triple_map[e1]
            triples_list.append(row)
            ent1_triple_map[e1] = triples_list
    
    
    pickle_file = open('ent1_triple_map', 'ab')
    
    pickle.dump(ent1_triple_map, pickle_file)
    
    pickle_file.close()
    triples_fp.close()
    
    
def main():
    triples_filepath = "/home/samir-pg/Knowledge_Graph/Battery_DB/triples.tsv"
    #gen_ent_triple_hashmap(triples_filepath)
    pickled_map_filepath = '/home/samir-pg/Knowledge_Graph/Distant_Supervision/ent1_triple_map'
    remove_duplicate_triples_V2(pickled_map_filepath)
    
    print("Hash-map generated successfully!")
    
main()
