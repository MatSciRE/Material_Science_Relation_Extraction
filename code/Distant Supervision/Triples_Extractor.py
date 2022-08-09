import gzip
import json
import os
import re
from collections import OrderedDict
import nltk
import operator
import random
import sys
import csv


def extract_triples_from_json(json_filepath : str, triples_filepath : str):
    triples_fp = open(triples_filepath, 'w')
    tsv_writer = csv.writer(triples_fp, delimiter='\t')
    json_fp = open(json_filepath, 'r')
    
    count = 0
    
    for line in json_fp:
        line = line.strip()
        try:
            items = json.loads(line)
            #print(len(item))
        except e:
            #print(e.message())
            continue
        
        #confirm the name of the method
        for item in items:
            try:
                name = item.get('Name')
                relation = item.get('Property')
                value = item.get('Value')
                unit = item.get('Unit')
                
                if(name==None or relation==None or value==None):
                    continue
                    
                if(unit==None):
                    tsv_writer.writerow([name , relation , value])
                else:    
                    tsv_writer.writerow([name , relation , value + " " + unit])
                
                count +=1
                if(count%100==0):
                    print('Entities read so far : ' + str(count))
                '''
                #debug
                if(count==5):
                    break
                '''
            except:
                continue
                
    triples_fp.close()
    json_fp.close()
    
    print('Number of triples extracted : ' + str(count))



def extract_triples_from_json_gen_stats(json_filepath : str, triples_filepath : str):
    triples_fp = open(triples_filepath, 'w')
    tsv_writer = csv.writer(triples_fp, delimiter='\t')
    json_fp = open(json_filepath, 'r')
    
    count = 0
    
    entities = dict()
    relations = dict()
    
    for line in json_fp:
        line = line.strip()
        try:
            items = json.loads(line)
            #print(len(item))
        except e:
            #print(e.message())
            continue
        
        #confirm the name of the method
        for item in items:
            try:
                name = item.get('Name')
                relation = item.get('Property')
                value = item.get('Value')
                unit = item.get('Unit')
                
                if(name==None or relation==None or value==None):
                    continue
                
                #Starting :: updating stats
                if(entities.get(name)==None):
                    entities[name] = 1
                else:
                    entities[name] += 1
                
                if(relations.get(relation)==None):
                    relations[relation] = 1
                else:
                    relations[relation] += 1
                
                #end :: updating stats
                
                if(unit==None):
                    tsv_writer.writerow([name , relation , value])
                else:    
                    tsv_writer.writerow([name , relation , value + " " + unit])
                
                count +=1
                if(count%100==0):
                    print('Entities read so far : ' + str(count))
                '''
                #debug
                if(count==5):
                    break
                '''
            except:
                continue
                
    triples_fp.close()
    json_fp.close()
    
    stats_fp = open('Statistics.txt', 'w')
    stats_fp.write('Total number of triples extracted : ' + str(count) + '\n\n\n')
    stats_fp.write('Extracted Relations\n')
    stats_fp.write('=================================\n')
    stats_fp.write('Number of Distinct relations : ' + str(len(relations.keys())))
    stats_fp.write("\n\n")
    for rel in relations.keys():
        stats_fp.write(str(rel) + ":" + str(relations[rel]) + "\n")
    
    
    stats_fp.write("\n\n\nExtracted Names\n")
    stats_fp.write("=================================\n")
    stats_fp.write('Number of Distinct Names : ' + str(len(entities.keys())))
    for ent in entities.keys():
        stats_fp.write(str(ent) + ":" + str(entities[ent]) + "\n")
    
    
    stats_fp.close()
    print('Number of triples extracted : ' + str(count))



def get_doi_from_json(json_filepath : str, doi_filepath : str):
    dois_fp = open(doi_filepath, 'w')
    #tsv_writer = csv.writer(triples_fp, delimiter='\t')
    json_fp = open(json_filepath, 'r')
    
    count = 0
    
    for line in json_fp:
        line = line.strip()
        try:
            items = json.loads(line)
            #print(len(item))
        except e:
            #print(e.message())
            continue
        
        #confirm the name of the method
        for item in items:
            try:
                #name = item.get('Name')
                #relation = item.get('Property')
                #value = item.get('Value')
                #unit = item.get('Unit')
                doi = item.get('DOI')
                
                if(doi==None):
                    continue
                    
                dois_fp.write(doi + '\n')
                count +=1
                if(count%100==0):
                    print('Entities read so far : ' + str(count))
                '''
                #debug
                if(count==5):
                    break
                '''
            except:
                continue
                
    dois_fp.close()
    json_fp.close()
    
    print('Number of DOIs extracted : ' + str(count))




def check_for_duplicates(filepath : str):
    fp = open(filepath, 'r')
    
    dois_map = dict()
    for line in fp.readlines():
        if(dois_map.get(line[:-1])==None):
            dois_map[line[:-1]] = 1
        else:
            #print('\nDuplicate found!\n')
            dois_map[line[:-1]] += 1
    
    fp2 = open('Unique_DOIs.txt', 'w')
    cnt = 1
    for doi in dois_map.keys():
        fp2.write(str(doi) + '\n')
        cnt+=1
    
    print('Total number of Unique DOIs : ' + str(cnt) + '\n')
    fp2.close()
    fp.close()


def main():
    json_filepath = "/home/samir-pg/Knowledge_Graph/Battery_DB/01-01-2020-3-Copy1.pdf.json"
    output_filepath = "/home/samir-pg/Knowledge_Graph/Battery_DB/triples1.tsv"
    output_dois_filepath = "/home/samir-pg/Knowledge_Graph/Battery_DB/dois1.txt"
    
    #extract_triples_from_json_gen_stats(json_filepath, output_filepath)
    #get_doi_from_json(json_filepath, output_dois_filepath)
    check_for_duplicates(output_dois_filepath)


main()
            
            
            
