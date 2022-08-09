# Material_Science_Relation_Extraction (MatSciRE)

MatSciRE is a tool for extracting entity1-relation-entity2 triplets from material science documents. The details of the model used can be found in the paper.

# Dataset

The annotated dataset is provided [here] (https://drive.google.com/drive/folders/1Tx-jHdTmGBb2XKtC_n5fOXG5w1pRxjFN?usp=sharing).

The code has been run on two platforms: server and Google Colab pro.

NVIDIA Tesla K40m GPU with 12
GB RAM, 6 Gbps clock cycle and GDDR5 memory. All the methods took less than 4 GPU hours for training. In server, pre-processing and pointer-network model (without BERT). For running the BERT models, CUDA version V11.1.105 has been used. Pytorch needs to be used.

Pytorch-transformers
Recordclass

The libraries can be installed with command - !pip install e.g. 

!pip install pytorch-transformers
!pip install recordclass

The version of the packages are pytorch-transformers-1.2.0 and recordclass-0.17.2. After the following statements, the following packages are installed.

boto3-1.24.32 
botocore-1.27.32 
jmespath-1.0.1 
pytorch-transformers-1.2.0 
s3transfer-0.6.0 
sacremoses-0.0.53 
sentencepiece-0.1.96 
urllib3-1.25.11
recordclass-0.17.2

The following import statements have been used.

import sys
import os
import numpy as np
import pandas as pd
import random
import matplotlib
import matplotlib.pyplot as plt

from collections import OrderedDict
import pickle
import datetime
import json
from tqdm import tqdm
from recordclass import recordclass
import math
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
torch.backends.cudnn.deterministic = True
from pytorch_transformers import BertTokenizer, BertModel, AdamW

import nltk
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import SpaceTokenizer


How the Code works
---------------------------------------
Generating dictionary from triplets
========================================
Input : 
    1. Json dump([Battery.json] (https://drive.google.com/file/d/16eqDPl61SiUMEwHgshwOvar5KcNJ-oQt/view?usp=sharing)) 

Output : 
    A dictionary of triples of the form is generated:
        dict['e1'] = list(triples that have 'e1' as entity_1)

Steps : 
    1. Run the Triples_Extractor.py file (located in "MatSciRE/Material_Science_Relation_Extraction/code/Distant Supervision") : 
        i.   Update the variable "json_filepath" to point to Battery.json. (if required)
        ii.  It generates "triples.tsv" as the output
            => see the description of the file for more details
            
    2. Run "generate_triples_hashmap.py" : 
        i.  Update the variable "triples_filepath" to point to Triples.tsv generated in the above step.
        ii. A pickle file named "unique_triples_map" would be created as output.
         
        The pickle file contains the required dictionary.

Generating Structured Dataset
=========================================
Input : 
    1. A corpus of papers in pdf format
    2. Dataset of triples(entity1, relation, entity2) [This is the dictionary we generated above]
    
Output : 
    Structured dataset in json form.

Code in "MatSciRE/Material_Science_Relation_Extraction/code/Distant Supervision"

Steps:

    1.  Convert pdf to json : Science-parse (https://github.com/allenai/science-parse) is used to convert materials science research papers from pdf to json.
    
    2.  Run Distant Supervision over the folder obtained in step 1:-
        StringBased_DS_v2.py: 
            i.   change "doc_path" to the folder containing the json files.
            ii.  change "output_filepath" to some suitable filename, this would be the output file.
            iii. Create a file named "Unique_doc_id_seed.txt" containing "0" (this is used to generate document Ids)
            iv.  Update the global variable "pickled_map_file" to point to "unique_triples_map" pickle file.
    
    3. Now create a folder (say named "OP_step_2") and place the file obtained as the output of  step (2) above inside this folder. In case, step 2 above was performed more than 1 time for different sets or batches of json file, meaning output of step 2 consists of more than 1 file, then place all the output files inside this folder "OP_step_2".
            
    4. Generate Structured dataset in json form using the output of distant supervision:-
        gen_structured_dataset.py : 
          i.   Update the variable "raw_input_folder" to point to "OP_step_2" folder created in step 3.
          ii.  Update the variable "after_preprocessing_folder" to point to an empty folder. This will contain the pre-processed files from raw_input_folder.
          iii. Create a file named "sent_id.txt" containing "0".(this is used to generate "id" part in structured dataset)
            
 The final output would be a single file named "Structured_dataset.jsonl" in the same folder as "gen_structured_dataset.py"
        

Training the Joint Extraction Model(Pointer Network model over Structured_dataset.jsonl)
=====================================================================
    All files are present in the folder "MatSciRE/Material_Science_Relation_Extraction/code"
    
    1. Divide the Structured_dataset.jsonl into train, dev and test sets
        run divide_dataset_in_dev_train_test.py :
            i.  Update the "input_filepath" to point to the "Structured_dataset.jsonl" file created in the previous section.
            ii. Update "dev_limit" and "test_limit" variables in the above code to the number of points in the dev and test set respectively.
            Three files (train.jsonl, test.jsonl and dev.jsonl) will be created as the output.
    
    2. Generate .sent, .pointer and .tup files for each of train.jsonl, test.jsonl and dev.jsonl
        run gen_dataset_for_JEModel.py : 
            1. Update the variable "input_filepath" to point to the train.jsonl file.
              Output : train.sent , train.pointer and train.tup files would be generated
            
            2. Repeat the above process for test.jsonl and dev.jsonl.
    
    3. Train the model for pointer-network model without BERT:
        "python3 ptrnet_decoder.py gpu_id random_seed source_data_dir target_data_dir train"
            source_data_dir => should be the the folder created by user.
        Test model:
         "python3 ptrnet_decoder.py gpu_id random_seed source_data_dir target_data_dir test"
            Please refer the following github page to understand more about how to train/test the model:-
                https://github.com/nusnlp/PtrNetDecoding4JERE
                
    4. For BERT, RoBERTa, MatBERT, SciBERT models, use helper.py to change the embeddings before running the models.
       Follow the MatBERT_Final.ipynb file for examples.
    
=============================== END ====================================

