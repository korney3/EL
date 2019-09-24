# Entity Linking

При решении задачи применения подхода [End2End](https://github.com/dalab/end2end_neural_el) к русскому языку было сделано:

1.  Парсинг дампа Википедии
2.  Создание файлов с информацией о базе знаний
3.  Эмуляция размеченного датасета
4.  Подсчет словаря частоты встречаемости mention: entities
5.  Форматирование words&entities embeddings из [Wikipedia2Vec](https://wikipedia2vec.github.io/wikipedia2vec/) для модели
6.  Запуск модели на русскоязычных данных

### Prerequisites

```
pip install -r requirements.txt
```

### Installing

Данные, нужные для запуска тренировки End2End модели можно скачать [здесь](https://drive.google.com/drive/folders/19KtVTKnQuF6ZMZ76NJZr2QT_5xHp5Mt6?usp=sharing). Для запуска модели см. пункт Running the End2end model.

При необходимости воспроизведения получения данных можно следовать инструкции ниже.

##### Парсинг дампа Википедии


1.   Скачать xml dump Википедии (например, [последний дамп русскоязычной википедии](http://dumps.wikimedia.org/ruwiki/latest/ruwiki-latest-pages-articles.xml.bz2))
2.   Извлечь текстовую информацию при помощи [Wikiextractor](https://github.com/attardi/wikiextractor) (not json option)
3.   Объединить все текстовые файлы в один 'textWithAnchorsFromAllWikipedia.txt' файл 

```
python3 WikiDumpTxt_join.py -p='./wiki' -o='textWithAnchorsFromAllWikipedia.txt'
```

где `./wiki` - путь к директории с викиэкстрактнутыми файлами.

##### Создание файлов с информацией о базе знаний

```
python3 wiki_info_create.py -p='./' -w='ruwiki-latest-pages-articles.xml'
```

где `./` - путь к xml дампу Википедии, а `ruwiki-latest-pages-articles.xml` - его имя.

```
mv wiki_name_id_map.txt ./wiki_data_generated
mv wiki_redirects.txt ./wiki_data_generated
mv wiki_disambiguation_pages.txt ./wiki_data_generated
python3 txt_to_json_conversion.py
```

В конце этого шага в папке 'wiki_data_generated' появляется набор файлов 'wiki_name_id_map' , 'wiki_redirects' и 'wiki_disambiguation_pages' в 'txt' и 'json' форматах.

##### Эмуляция размеченного датасета

1.  Делим текстовый дамп Википедии на отдельные статьи с названиями формата 'id_12345.txt'

```
python3 wiki_dump_separate.py -p='./wiki_articles' -f='textWithAnchorsFromAllWikipedia.txt'
```

2.  Обрабатываем полученные файлы, приводя их к формату используемого моделью датасета

| Оригинальный датасет | Полученный датасет |
| ------ | ------ |
| DOCSTART_69_London | DOCSTART_2058943_иванчуковка |
| MMSTART_17867 | Иванчуковка | 
| London | MMSTART_9820 | 
| MMEND | село| 
| shipsales | MMEND | 
| *NL* | *NL* | 


Поскольку количество статей, необхдимых обработать ~1.5 млн статей, для оптимизации используется распараллеливание препроцессинга.

```
mpiexec -n=4 python -m mpi4py wiki_dataset_parallel.py
```

где '-n' - количество работающих процессов.

Результатом работы скрипта будет набор текстовых файлов, из которых можно собирать датасет и набор 'json'-файлов с частотой встречаний упоминание:сущность.

##### Приведение Words&Entities Embeddings к нужному формату

Файл с pretrained Wikipedia2Vec embeddings можно скачать [здесь](http://wikipedia2vec.s3.amazonaws.com/models/ru/2018-04-20/ruwiki_20180420_300d.pkl.bz2). 

Делим файл на word embeddings и entity embeddings.

```
python3 word_ent_embed_split.py
```

##### Создание файла с именами людей(персон)

Перейти в [экспорт статей](https://ru.wikipedia.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:%D0%AD%D0%BA%D1%81%D0%BF%D0%BE%D1%80%D1%82) и в поле 'Добавить страницы из категории:' вставить категорию 'Персоналии по алфавиту'.

Текст из окна добавить в файл 'persons.txt'.

Отформатировать полученный файл.

```
python3 persons_format.py
```


## Running the End2end model

1. Скачать [End2End](https://github.com/dalab/end2end_neural_el) репозиторий. 
2. Заменить файлы 'prepro_util.py' и 'util.py' из 'code/preprocessing' на расположенные в end2end директории.
3. Если данные не были созданы по инструкции выше, скачать и распаковать в соответствующие папки [здесь](https://drive.google.com/drive/folders/19KtVTKnQuF6ZMZ76NJZr2QT_5xHp5Mt6?usp=sharing)
4. Нужно поместить созданные файлы в соответствующие места в End2End репозитории

```
cp ./wiki_data_generated/wiki_disambiguation_pages.txt ./end2end/data/basic_data
cp ./wiki_data_generated/wiki_redirects.txt ./end2end/data/basic_data
cp ./wiki_data_generated/wiki_disambiguation_pages.txt ./end2end/data/basic_data
cp ./wiki_data_generated/persons.txt ./end2end/data/basic_data

cp ./data_generated/word2vec ./end2end/data/basic_data/wordEmbeddings/Word2Vec/
```

5. Создать тренировочный датасет

```
python3 emulate_data.py -n=10
```

где '-n' - количество статей, сложенных в датасет. Полученные файлы сохранены в './emulated_data'

Поместить полученные файлы в соответствующие директории.

```
cp ./emulated_data/prob_yago_crosswikis_wikipedia_p_e_m.txt ./end2end/data/basic_data/\

cp ./emulated_data/ent_vecs.npy ./end2end/data/entities/ent_vecs/
cp ./emulated_data/wikiid2nnid.txt ./end2end/data/entities/wikiid2nnid/
cp ./emulated_data/nnid2wikiid.txt ./end2end/data/entities/wikiid2nnid/

cp ./emulated_data/aida_train.txt ./end2end/data/new_datasets/
```

6. Запустить обработку созданных данных

```
python -m preprocessing.prepro_util --create_entity_universe True --lowercase_p_e_m True --lowercase_spans True
python -m preprocessing.prepro_util
```

7. Запустить тренировочный эксперимент (см. инструкцию в официальном репозитории)

```
export v=1
python3 -m model.train --batch_size=4 --experiment_name=corefmerge --training_name=group_global/global_model_v$v --ent_vecs_regularization=l2dropout --evaluation_minutes=10 --nepoch_no_imprv=6 --span_emb="boundaries" --dim_char=50 --hidden_size_char=50 --hidden_size_lstm=150 --nn_components=pem_lstm_attention_global --fast_evaluation=True --all_spans_training=True --attention_ent_vecs_no_regularization=True --final_score_ffnn=0_0 --attention_R=10 --attention_K=100 --train_datasets=aida_train --el_datasets=aida_train --el_val_datasets=0 --global_thr=0.001 --global_score_ffnn=0_0 --continue_training=True
```

8. По оканчании тренировки можно запустить gerbil server для evaluation модели

```
python -m gerbil.server --training_name=group_global/global_model_v$v --experiment_name=corefmerge --persons_coreference_merge=True --all_spans_training=True
```

