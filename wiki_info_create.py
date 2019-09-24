import argparse

ap = argparse.ArgumentParser()

ap.add_argument("-p", "--path_wiki_xml", default='./',type = str,
   help="path to Wiki xml dump")
ap.add_argument("-w", "--filename_wiki", default='ruwiki-latest-pages-articles.xml',type = str,
   help="Name of Wiki xml dump")
ap.add_argument("-a", "--filename_articles", default='wiki_name_id_map.csv',type = str,
   help="Output filename of wiki id-name map")
ap.add_argument("-r", "--filename_redirect", default='wiki_redirects.csv',type = str,
   help="Output filename of wiki redirected pages")
ap.add_argument("-d", "--filename_disambig", default='wiki_disambiguation_pages.csv',type = str,
   help="Output filename of wiki disambiguation pages")
ap.add_argument("-e", "--encoding", default='utf-8',type = str,
   help="Encoding of files")



args = ap.parse_args()

from wiki_data_generated.wiki_info_generation import wiki_txt_files_creating

wiki_txt_files_creating(PATH_WIKI_XML = args.path_wiki_xml,
    FILENAME_WIKI = args.filename_wiki,
    FILENAME_ARTICLES = args.filename_articles,
    FILENAME_REDIRECT = args.filename_redirect,
    FILENAME_DISAMBIG = args.filename_disambig,
    ENCODING = args.encoding)