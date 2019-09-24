import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-p", "--path_articles", default='./wiki_articles',type = str,
   help="path to save obtained articles")
ap.add_argument("-f", "--filename", default='textWithAnchorsFromAllWikipedia2014Feb.txt',type = str,
   help="Name of Wiki txt dump")



args = ap.parse_args()

from wiki_data_generated.wiki_info_generation import creating_several_txt_files_from_wiki_txt_dump

creating_several_txt_files_from_wiki_txt_dump(path = args.path_articles,
                                                  filename = args.filename)