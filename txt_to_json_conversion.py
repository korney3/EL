from wiki_data_generated.wiki_info_generation import wiki_name_id_txt_to_json

wiki_name_id_txt_to_json(PATH='./wiki_data_generated', 
                            FILENAME_ARTICLES = 'wiki_name_id_map.txt')

wiki_name_id_dict_redir = {}
wiki_id_name_dict_redir = {}
with open ('./wiki_data_generated/wiki_name_id_map.txt','r') as f:
    for s in f:
        line = s.split('\n')[0]
        wiki_title,wiki_id = line.split('\t')
        wiki_title = wiki.lower()
        if wiki_title in wiki_redirects.keys() and wiki_redirects[wiki_title] in wiki_name_id_dict.keys():
            wiki_name_id_dict_redir[wiki_title] = wiki_name_id_dict[wiki_redirects[wiki_title]]
            wiki_id_name_dict_redir[wiki_id] = wiki_redirects[wiki_title]
        else:
            wiki_name_id_dict_redir[wiki_title] = wiki_id
            wiki_id_name_dict_redir[wiki_id] = wiki_title 
wiki_name_id_json = json.dumps(wiki_name_id_dict_redir)
f = open("./wiki_data_generated/wiki_name_id_with_redirections.json","w")
f.write(wiki_name_id_json)
f.close()
wiki_id_name_json = json.dumps(wiki_id_name_dict_redir)
f = open("./wiki_data_generated/wiki_id_name_with_redirections.json","w")
f.write(wiki_id_name_json)
f.close()
from wiki_data_generated.wiki_info_generation import wiki_redirections_txt_to_json
wiki_redirections_txt_to_json(PATH='./wiki_data_generated', 
                            FILENAME_REDIRECTIONS = 'wiki_redirects.txt')