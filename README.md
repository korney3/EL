# Entity Linking

Applying [End2End](https://github.com/dalab/end2end_neural_el) approach to Entity Linking (EL) task in russian language.

The code solves several tasks:

1.  Parsing of Russian Wikipedia dump
2.  Creating files with info about knowledge base (KB, Wikipedia)
3.  Emulation of marked dataset used in End2End approach
4.  Calculating dictionary of mention: entities frequency
5.  Formatting of words&entities embeddings from [Wikipedia2Vec](https://wikipedia2vec.github.io/wikipedia2vec/) for the model
6.  Running the model with Russian language data

### Prerequisites

```
pip install -r requirements.txt
```

### Installing

Data needed for running End2End model training can be downloaded here [здесь](https://drive.google.com/drive/folders/19KtVTKnQuF6ZMZ76NJZr2QT_5xHp5Mt6?usp=sharing). For running of the model go to "Running the End2end model" part.

For reproducing data obtaining one can follow instruction below.

##### Wikipedia dump parsing


1.  Download Wikipedia dump (for example, [last dump of russian Wikiedia](http://dumps.wikimedia.org/ruwiki/latest/ruwiki-latest-pages-articles.xml.bz2))
2.   Extract text info by [Wikiextractor](https://github.com/attardi/wikiextractor) (not json option)
3.   Join all the text files in one 'textWithAnchorsFromAllWikipedia.txt' file

```
python3 WikiDumpTxt_join.py -p='./wiki' -o='textWithAnchorsFromAllWikipedia.txt'
```

where `./wiki` - path to wikiextracted files.

##### Creating files with nfo about knowledge base

```
python3 wiki_info_create.py -p='./' -w='ruwiki-latest-pages-articles.xml'
```

where `./` - path to Wikipedia dump xml file and `ruwiki-latest-pages-articles.xml` is its name.

```
mv wiki_name_id_map.txt ./wiki_data_generated
mv wiki_redirects.txt ./wiki_data_generated
mv wiki_disambiguation_pages.txt ./wiki_data_generated
python3 txt_to_json_conversion.py
```

In the end of the step there will be created set of files 'wiki_name_id_map' , 'wiki_redirects' и 'wiki_disambiguation_pages' in 'txt' and 'json' formats in 'wiki_data_generated' directory.

##### Emulation of marked datasets

1.  Split text Wikipedia Dump into separate articles with names like 'id_12345.txt'

```
python3 wiki_dump_separate.py -p='./wiki_articles' -f='textWithAnchorsFromAllWikipedia.txt'
```

2.  Preprocess obtained files, leading them to the format used in End2End model

| Original dataset | Obtained dataset |
| ------ | ------ |
| DOCSTART_69_London | DOCSTART_2058943_иванчуковка |
| MMSTART_17867 | Иванчуковка | 
| London | MMSTART_9820 | 
| MMEND | село| 
| shipsales | MMEND | 
| *NL* | *NL* | 


As number of articles to be preprocessed is about ~1.5 mln articles there is used parallelization of preprocessing for the optimization.

```
mpiexec -n=4 python -m mpi4py wiki_dataset_parallel.py
```

where '-n' is amount of working processes.

The result of script is a set of text files, that can be collected into dataset, and a set of 'json'-files with frequencies if mention:entity.

##### Leading Words&Entities Embeddings to needed format

File with thr pretrained Wikipedia2Vec embeddings can be downloaded [here](http://wikipedia2vec.s3.amazonaws.com/models/ru/2018-04-20/ruwiki_20180420_300d.pkl.bz2). 

Separate obtained file into word embeddings and entity embeddings.

```
python3 word_ent_embed_split.py
```

##### Creating file with persons' names

Go to [articles export](https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%AD%D0%BA%D1%81%D0%BF%D0%BE%D1%80%D1%82) and put into the field 'Добавить страницы из категории:' category 'Персоналии по алфавиту'.

TAdd the text from the window to the file 'persons.txt'.

Format obtained file.

```
python3 persons_format.py
```


## Running the End2end model

1. Download [End2End](https://github.com/dalab/end2end_neural_el) repository. 
2. Replace 'prepro_util.py' and 'util.py' files from 'code/preprocessing' with files located in end2end dir.
3. If data hasn't been created wia instruction above, download and unpack it to the appropriate directories from [here](https://drive.google.com/drive/folders/19KtVTKnQuF6ZMZ76NJZr2QT_5xHp5Mt6?usp=sharing)
4. Place created files to appropriate directories in End2End repository

```
cp ./wiki_data_generated/wiki_disambiguation_pages.txt ./end2end/data/basic_data
cp ./wiki_data_generated/wiki_redirects.txt ./end2end/data/basic_data
cp ./wiki_data_generated/wiki_disambiguation_pages.txt ./end2end/data/basic_data
cp ./wiki_data_generated/persons.txt ./end2end/data/basic_data

cp ./data_generated/word2vec ./end2end/data/basic_data/wordEmbeddings/Word2Vec/
```

5. Create training dataset

```
python3 emulate_data.py -n=10
```

where '-n' is the amount of articles in the dataset. Obtained files are located in './emulated_data'

Move obtained files in appropriate directories.

```
cp ./emulated_data/prob_yago_crosswikis_wikipedia_p_e_m.txt ./end2end/data/basic_data/\

cp ./emulated_data/ent_vecs.npy ./end2end/data/entities/ent_vecs/
cp ./emulated_data/wikiid2nnid.txt ./end2end/data/entities/wikiid2nnid/
cp ./emulated_data/nnid2wikiid.txt ./end2end/data/entities/wikiid2nnid/

cp ./emulated_data/aida_train.txt ./end2end/data/new_datasets/
```

6. Run preprocessing of created data.

```
python -m preprocessing.prepro_util --create_entity_universe True --lowercase_p_e_m True --lowercase_spans True
python -m preprocessing.prepro_util
```

7. Run training experiment (follow the instructions in the official repository)

```
export v=1
python3 -m model.train --batch_size=4 --experiment_name=corefmerge --training_name=group_global/global_model_v$v --ent_vecs_regularization=l2dropout --evaluation_minutes=10 --nepoch_no_imprv=6 --span_emb="boundaries" --dim_char=50 --hidden_size_char=50 --hidden_size_lstm=150 --nn_components=pem_lstm_attention_global --fast_evaluation=True --all_spans_training=True --attention_ent_vecs_no_regularization=True --final_score_ffnn=0_0 --attention_R=10 --attention_K=100 --train_datasets=aida_train --el_datasets=aida_train --el_val_datasets=0 --global_thr=0.001 --global_score_ffnn=0_0 --continue_training=True
```

8. After the finishing of training it's possible to run the gerbil server for model evaluation.
```
python -m gerbil.server --training_name=group_global/global_model_v$v --experiment_name=corefmerge --persons_coreference_merge=True --all_spans_training=True
```

