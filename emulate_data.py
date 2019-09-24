import os
import random
import json
from wiki_data_generated.wiki_info_generation import merge_filenames,merge_jsons
import time
import numpy as np
import unicodedata
# import matplotlib.pyplot as plt

import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-d", "--dataset_dir", default='./wiki_dataset_articles',type = str,
   help="Folder with Wikipedia articles in 'aida_train.txt' format")
ap.add_argument("-n", "--num_articles", default=500,type = int,
   help="Amount of articles put to dataset")
ap.add_argument("-w", "--wiki_dict_path", default="./wiki_data_generated",type = str,
   help="Path to dictionary with wiki_id-wiki_name and wiki_name-wiki_id mapping")
ap.add_argument("-e", "--ent_embed_path", default="./data_generated",type = str,
   help="Path to entity embeddings")
ap.add_argument("-o", "--output_path", default="./emulated_data",type = str,
   help="Output data path")

args = ap.parse_args()

DATASET_DIR = args.dataset_dir
NUM_ARTICLES = args.num_articles
WIKI_DICT_PATH = args.wiki_dict_path
ENT_EMBED_PATH = args.ent_embed_path
OUTPUT_PATH = args.output_path

step = int(NUM_ARTICLES/1000)+1


filenames = os.listdir(DATASET_DIR)
filenames = [filename for filename in filenames if '.txt' in filename]
ids = [filename.split('.')[0].split('_')[1] for filename in filenames]

dataset = random.sample(ids, NUM_ARTICLES)

txts=['id_'+wiki_id+'.txt' for wiki_id in dataset]
jsons=['id_'+wiki_id+'_e_m_counts.json' for wiki_id in dataset]

print('Start loading needed files')
with open (os.path.join(WIKI_DICT_PATH,'wiki_id_name_with_redirections.json')) as json_file:
    wiki_id_name_dict = json.load(json_file)

with open (os.path.join(WIKI_DICT_PATH,"wiki_name_id_with_redirections.json")) as json_file:
    wiki_name_id_dict = json.load(json_file)
    
print('Done')

print('Start "aida_train.txt" dataset creation')

merge_filenames(path=DATASET_DIR, filenames_input=txts, 
                    filename_output=os.path.join(OUTPUT_PATH,"aida_train.txt"),
                    filler_start='DOCSTART',
                    filler_end='DOCEND',
                    add_id=True, 
                    wiki_id_name_dict=wiki_id_name_dict,
                    num_of_files=NUM_ARTICLES)

print('Done')

print('Start p(e|m) count creation')

wiki_p_e_m = merge_jsons(path=DATASET_DIR, filenames=jsons, 
                filename=os.path.join(OUTPUT_PATH,'prob_yago_crosswikis_wikipedia_p_e_m.txt'),
                filetype='.json',
                wiki_id_name_dict=wiki_id_name_dict, 
                step=step)

disambiguations = []
for mention in wiki_p_e_m.keys():
    disambiguations.append(len(wiki_p_e_m[mention].keys()))

# plt.figure(figsize=(20,10))
# plt.hist(disambiguations,log=True,bins=100)
# plt.xticks(fontsize=20)
# plt.yticks(fontsize=20)
# plt.title('Distribution of disambiguation in dataset',fontsize=25)
# plt.text(max(disambiguations)*0.5,10**4,'Overall mentions\nnumber = '+str(len(wiki_p_e_m.keys())),fontdict={'fontsize':25})
# plt.show()

print('Done')

entities={}
for mention in wiki_p_e_m.keys():
    for entity in wiki_p_e_m[mention].keys():
        if entity in entities:
            entities[entity]+=wiki_p_e_m[mention][entity]
        else:
            entities[entity]=wiki_p_e_m[mention][entity]
            
needed_entities = list(entities.keys())

print('Start entity embedding creation')

entity_embed = np.zeros(shape=(1,300))
overall_num = 1035084
from my_funcs import print_progress_stats
with open(os.path.join(OUTPUT_PATH,'logs_embeddigs_err'),'w') as logs:
    logs.write('\t'.join(['Number of iterations','Number of words','Wrong key']))
entities=[]
with open(os.path.join(ENT_EMBED_PATH,"ent2vec"),'r') as f:
    with open(os.path.join(OUTPUT_PATH,'nnid2wikiid.txt'),'w') as nn_to_wiki:
        with open(os.path.join(OUTPUT_PATH,'wikiid2nnid.txt'),'w') as wiki_to_nn:
            num = 0
            start = time.time()
            wiki_to_nn_text=''
            nn_to_wiki_text=''
            for i,s in enumerate(f):
                if i==0:
                    overall_num = int(s.strip().split(' ')[0])
                    nn_to_wiki_text+=(str(num)+'\t'+"1"+'\n')
                    wiki_to_nn_text+=("1"+'\t'+str(num)+'\n')
                    num+=1
                    continue
                data = s.split('\n')[0].split(' ')
                word = data[0].lower().replace('_',' ')
                word = unicodedata.normalize('NFKC',word)
                vector = np.array(list(map(lambda x: float(x),data[1:])))
                if word in wiki_name_id_dict.keys() and word not in entities:
                    if wiki_name_id_dict[word] in needed_entities:
                        entity_embed=np.vstack([entity_embed,vector])
                        nn_to_wiki_text+=(str(num)+'\t'+wiki_name_id_dict[word]+'\n')
                        wiki_to_nn_text+=(wiki_name_id_dict[word]+'\t'+str(num)+'\n')
                        num+=1
                        entities.append(word)
                    else:
                        pass
                else:
                    with open(os.path.join(OUTPUT_PATH,'logs_embeddigs_err'),'a') as logs:
                        logs.write(str(i)+'\t'+str(num)+'\t'+word+'\n')
                if i%10000==0:
                    nn_to_wiki.write(nn_to_wiki_text)
                    wiki_to_nn.write(wiki_to_nn_text)
                    nn_to_wiki_text=''
                    wiki_to_nn_text=''
                    np.save(os.path.join(OUTPUT_PATH,'ent_vecs.npy'),entity_embed)
                    print (i,'/',overall_num,'(',round(float(i)/overall_num*100),'%)',num)
                    print_progress_stats (overall_num, i, 0, time_per_iteration=round((time.time()-start)/60/i,3), num_of_processes=1)
with open(os.path.join(OUTPUT_PATH,'nnid2wikiid.txt'),'w') as nn_to_wiki:
        with open(os.path.join(OUTPUT_PATH,'wikiid2nnid.txt'),'w') as wiki_to_nn:
            nn_to_wiki.write(nn_to_wiki_text)
            wiki_to_nn.write(wiki_to_nn_text)
np.save(os.path.join(OUTPUT_PATH,'ent_vecs.npy'),entity_embed)
print('Done')