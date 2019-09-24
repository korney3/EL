#!/usr/bin/env python
from __future__ import print_function

from mpi4py import MPI
import json
import os
import re
from itertools import compress
from urllib.request import urlopen
from urllib import request
from urllib.parse import unquote
import pymorphy2
import unicodedata
import json
from html.parser import HTMLParser
from nltk.tokenize import wordpunct_tokenize,sent_tokenize
import nltk
# nltk.download('punkt')
import unidecode
import time
import sys

def enum(*sequential, **named):
    """Handy way to fake an enumerated type in Python
    http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# Define MPI message tags
tags = enum('READY', 'DONE', 'EXIT', 'START')

# Initializations and preliminaries
comm = MPI.COMM_WORLD   # get MPI communicator object
size = comm.size        # total number of processes
rank = comm.rank        # rank of this process
status = MPI.Status()   # get MPI status object
print('dlkdf')

if rank == 0:
    # Master process executes code below
    if os.path.isfile('./logs_wiki_articles.txt'):
        pass
    else:
        with open('./logs_wiki_articles.txt','w') as f_log:
            f_log.write('\t'.join(['Article id','Number of processed strings','Number of extracted mentions','Wasted time, min']))
            f_log.write('\n')
    file_ids = list(map(lambda x: int((x.split('.')[0]).split('_')[1]) if x!= '.ipynb_checkpoints' else '',os.listdir(path='./wiki_articles')))
#     file_ids=[100002,
#  100010,
#  100013,
#  100019,
#  10002,
#  100020,
#  100022,
#  1000232,
#  100024,
#  100026]
    print('rank 0')
    try:
        file_ids.remove('')
    except ValueError:
        pass
    file_ids_done = list(map(lambda x: int((x.split('.')[0]).split('_')[1]) if x!= '.ipynb_checkpoints' and x.split('.')[1]!='json' else '',os.listdir(path='./wiki_dataset_articles')))
    tasks = [x for x in file_ids if x not in file_ids_done]
    task_index = 0
    num_workers = size - 1
    closed_workers = 0
    print("Master starting with %d workers" % num_workers)
    while closed_workers < num_workers:
        res = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        source = status.Get_source()
        tag = status.Get_tag()
        if tag == tags.READY:
            # Worker is ready, so send it a task
            if task_index < len(tasks):
                comm.send(tasks[task_index], dest=source, tag=tags.START)
                task_index += 1
            else:
                comm.send(None, dest=source, tag=tags.EXIT)
        elif tag == tags.DONE:
#             {'number_of_strings':i,'number_of_mentions': num_mentions,'wasted_time':time.time()-start}
            task,result = res
            num_strings = result['number_of_strings']
            num_mentions = result['number_of_mentions']
            wasted_time = round(float(result['wasted_time'])/60,3)
            if num_strings==0 and num_mentions==0 and wasted_time==0:
                err = result['err']
                with open('./logs_wiki_articles_errors.txt','a') as f_err:
                    f_err.write(str(task)+'\t'+'\t'.join(err)+'\n')
                
            else:
                with open('./logs_wiki_articles.txt','a') as f_log:
                    f_log.write('\t'.join([str(task),str(num_strings),str(num_mentions),str(wasted_time)]))
                    f_log.write('\n')
        elif tag == tags.EXIT:
            print("Worker %d exited." % source)
            closed_workers += 1
    print("Master finishing")
else:
    # Worker processes execute code below
    class MyHTMLParser(HTMLParser):
        def __init__(self):
            self.entities=[]
            self.mentions=[]
            self.text=[]
            self.start=False
            self.id = 0
            self.mentions_ids=[]
            super().__init__()

        def handle_starttag(self, tag, attrs):
            self.start=True
            if tag == 'a':
                attrs=dict(attrs)
                attrs = attrs['href'] 
                entity = unquote(attrs)
                self.entities.append(entity.lower())

        def handle_endtag(self, tag):
            self.start=False

        def handle_data(self, data):
            self.text.append(data)

            if self.start:
                self.mentions.append(data)
                self.mentions_ids.append(self.id)
            self.id +=1

    def extract_text_and_hyp(line):
        no_dots = line.replace('.','')
        if line[-1]=='.':
            line = no_dots+'.'
        else:
            line = no_dots
        line = unicodedata.normalize('NFKC',line)
        line = ''.join((c for c in line if unicodedata.category(c) != 'Mn'))
        parser = MyHTMLParser()
        parser.feed(line)
        mask = [mention.find('Wikipedia')==-1 and mention.find('Wikipedia')==-1 and len(mention)>=1 for mention in parser.mentions]
        parser.entities = list(map(lambda x: wiki_redirects_names[x] if x in wiki_redirects_names.keys() else x,parser.entities))
        parser.entities=list(map(lambda x: re.sub('&amp;', '&',re.sub("^%s*(.-)%s*$", "%1", x)),parser.entities))
        mask = [entity.find('#')==-1 and mask_prev for mask_prev,entity in zip(mask,parser.entities)]
        entities_id = list(map(lambda x: wiki_name_id_dict[x] if x in wiki_name_id_dict.keys() else str(-1),parser.entities))
        mask = [str(ent_id) not in wiki_disambiguation.keys() and bool(int(ent_id)+1) and mask_prev for mask_prev,ent_id in zip(mask,entities_id)]
        parser.entities = list(compress(parser.entities,mask))
        parser.mentions = list(compress(parser.mentions,mask))
        parser.mentions_ids = list(compress(parser.mentions_ids,mask))
        entities_id = list(compress(entities_id,mask))

        morph = pymorphy2.MorphAnalyzer()
        parser.mentions = list(map(lambda word: ' '.join(list(map(lambda x: morph.parse(x)[0].normal_form  if len(x)>2 and 'Name' not in morph.parse(x)[0].tag and 'Surn' not in morph.parse(x)[0].tag  else x, wordpunct_tokenize(word)))), parser.mentions))

        text=''.join([data if i not in parser.mentions_ids else ' MMSTART_'+str(entities_id[parser.mentions_ids.index(i)])+' '+data+' MMEND ' for i,data in enumerate(parser.text)])
        sentences = sent_tokenize(text)
        sentences = ' NL '.join(sentences)
        text = ['*NL*' if token=='NL' else token for token in wordpunct_tokenize(sentences)]
        try:
            if text[-1]!='*NL*':
                text=text+['*NL*']
        except IndexError:
            pass
        return parser.entities,parser.mentions,entities_id,parser.text,parser.mentions_ids, text
    name = MPI.Get_processor_name()
    print("I am a worker with rank %d on %s." % (rank, name))
    with open ("./wiki_data_generated/wiki_name_id_with_redirections.json") as json_file:
        wiki_name_id_dict = json.load(json_file)
    with open ("./wiki_data_generated/wiki_id_name_with_redirections.json") as json_file:
        wiki_id_name_dict = json.load(json_file)
    with open ("./wiki_data_generated/wiki_redirects_names.json") as json_file:
        wiki_redirects_names = json.load(json_file)
    wiki_disambiguation = {}
    with open('./wiki_data_generated/wiki_disambiguation_pages.txt','r',encoding='utf-8') as f:
        for s in f:
            wiki_id, wiki_name= s.rstrip().split('\t')
            wiki_name=wiki_name.lower()
            wiki_disambiguation[wiki_id]=wiki_name
    print('Done import')
    while True:
        comm.send(None, dest=0, tag=tags.READY)
        task = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        tag = status.Get_tag()
        if tag == tags.START:
            wiki_e_m_counts = {}
#             print(task, rank)
            filename_input = 'id_'+str(task)+'.txt'
            filename_output = './wiki_dataset_articles/'+filename_input
            filename_output_json = './wiki_dataset_articles/id_'+str(task)+'_e_m_counts.json'
            wiki_e_m_counts['num_strings'] = 0
            wiki_e_m_counts['num_mentions'] = 0
            num_strings = 0
            num_mentions = 0
            start = time.time()
            wiki_e_m_counts={}
            try:
                with open('./wiki_articles/'+filename_input,'r',encoding='utf-8') as f:
                    for i,s in enumerate(f):
                        sentences = sent_tokenize(s)
                        for sentence in sentences:
                            entities,mentions,entities_id,_,_,text = extract_text_and_hyp(sentence)
                            with open(filename_output,'a',encoding='utf-8') as train:
                                train.write('\n'.join(text))
                                train.write('\n')
                            if len(entities)>0:
                                for ent_id,mention in zip(entities_id,mentions):
                                    if mention not in wiki_e_m_counts:
                                        wiki_e_m_counts[mention]={}
                                    if ent_id not in wiki_e_m_counts[mention]:
                                        wiki_e_m_counts[mention][ent_id]=0
                                    wiki_e_m_counts[mention][ent_id]+=1
                            num_mentions+=len(mentions)
                            wiki_e_m_counts['num_strings']=i
                            wiki_e_m_counts['num_mentions']=num_mentions
                        wiki_e_m_counts_json = json.dumps(wiki_e_m_counts)
                        f = open(filename_output_json,"w")
                        f.write(wiki_e_m_counts_json)
                        f.close()
                result =  {'number_of_strings':i,'number_of_mentions': num_mentions,'wasted_time':time.time()-start} 
            except Exception as esd:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                result =  {'number_of_strings':0,'number_of_mentions':0,'wasted_time':0, 'err': [str(exc_type), str(exc_tb.tb_lineno)]}
            comm.send([task,result], dest=0, tag=tags.DONE)
        elif tag == tags.EXIT:
            break
    comm.send(None, dest=0, tag=tags.EXIT)
