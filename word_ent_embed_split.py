import argparse
import os

ap = argparse.ArgumentParser()

ap.add_argument("-p", "--wiki2vec_path", default='./',type = str,
   help="path to wikipedia2vec bin file")
ap.add_argument("-f", "--filename", default='ru_entities.bin',type = str,
   help="Name of wikipedia2vec bin file")
ap.add_argument("-o", "--output_path", default='./data_generated',type = str,
   help="Path for storing resulted ent2vec and word2vec files")

args = ap.parse_args()

WIKI2VEC_PATH = './'
WIKI2VEC_FILENAME = 'ru_entities.bin'
OUTPUT_PATH='./data_generated'


words = 0
entities = 0
with open(os.path.join(WIKI2VEC_PATH,WIKI2VEC_FILENAME),'r') as f:
    for i,s in enumerate(f):
        if i==0:
            continue
        data = s.split('\n')[0].split(' ')
        word = data[0]
        if 'ENTITY/'in word:
            entities+=1
        else:
            words+=1
       
words_done=0
entities_done=0
with open(os.path.join(WIKI2VEC_PATH,WIKI2VEC_FILENAME),'r') as f:
    with open(os.path.join(OUTPUT_PATH,'word2vec'),'w') as word_dict:
        with open(os.path.join(OUTPUT_PATH,'ent2vec'),'w') as entity_dict:
            for i,s in enumerate(f):
                if i==0:
                    word_dict.write(str(words)+' '+str(300)+'\n')
                    entity_dict.write(str(entities)+' '+str(300)+'\n')
                    continue
                data = s.split('\n')[0].split(' ')
                word = data[0]
                vector = data[1:]
                if 'ENTITY/'in word:
                    entity=word[7:]
                    line = ' '.join([entity]+vector)
                    entity_dict.write(line)
                    entity_dict.write('\n')
                    entities_done+=1
                else:
                    line = ' '.join([word]+vector)
                    word_dict.write(line)
                    word_dict.write('\n')
                    words_done+=1
                    
                if i%100000==0:
                    print(i, words_done, entities_done)