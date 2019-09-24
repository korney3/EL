import argparse
import os

ap = argparse.ArgumentParser()

ap.add_argument("-p", "--path_persons", default='./',type = str,
   help="path to init persons.txt file")
ap.add_argument("-o", "--path_output", default='./wiki_data_generated',type = str,
   help="path to output persons.txt file")

args = ap.parse_args()

with open(os.path.join(args.path_persons,'persons.txt'),'r',encoding='utf-8') as fin:
    with open(os.path.join(args.path_output,'./persons.txt'),'w',encoding='utf-8') as fout:
        for i,s in enumerate(fin):
            name = ' '.join(s.split('\n')[0].split('_'))
            if ',' in name:
                name = ' '.join(name.split(',')[::-1])
            fout.write(name.strip()+'\n')
        