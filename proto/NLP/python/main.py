import argparse
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import nltk as nl
import numpy as np
# https://github.com/cmchurch/nltk_french/blob/master/french-nltk.py
# https://nlp.stanford.edu/software/tagger.shtml 

# Link to POS tagger from Stanford
# https://nlp.stanford.edu/software/stanford-tagger-4.2.0.zip 

from nltk.tag.stanford import StanfordPOSTagger
import os

# Method to download + extract found here https://stackoverflow.com/questions/64990197/download-and-extract-zip-file 
def download_extract_zip(zip_url:str,download_path:str):
    with urlopen(zip_url) as zipresp:
        with ZipFile(BytesIO(zipresp.read())) as zfile:
            zfile.extractall(download_path)

def update_packages():
    nl.data.path.append("./nltk_data")
    os.makedirs("nltk_data",exist_ok=True)
    if(not os.path.exists("./nltk_data/tokenizers/punkt")):
        nl.download("punkt",download_dir="./nltk_data")
    if(not os.path.exists("./nltk_data/chunkers/maxent_ne_chunker")):
        nl.download('maxent_ne_chunker',download_dir="./nltk_data")
    if(not os.path.exists("./nltk_data/corpora/words")):
        nl.download('words',download_dir="./nltk_data")
    if(not os.path.exists("./nltk_data/taggers/averaged_perceptron_tagger")):
        nl.download('averaged_perceptron_tagger',download_dir="./nltk_data")
    if(not os.path.exists("./nltk_data/stanford-postagger-full-2020-11-17")):
        print("Downloading Stanford Part-Of-Speech Tagger")
        download_extract_zip("https://nlp.stanford.edu/software/stanford-tagger-4.2.0.zip","./nltk_data/")

def process_sentences(file_content_string: str):
    chunk_patterns = r"""
            DATE: {<DET>?<NUM><NOUN><NUM>?}
            """
    sports_dictionnary = {"tennis","Tennis"}
    chunk_parser = nl.chunk.RegexpParser(chunk_patterns)
    for sent in nl.sent_tokenize(file_content_string,language='french'):
        print("NEXT SENTENCE:\n")
        # Voir si possibilité d'utiliser un NER chunker différent pour détecter des dates, sports etc
        for chunk in chunk_parser.parse(taggerModel.tag(nl.word_tokenize(sent,language="french"))):
            type = chunk[1]
            if chunk[0] in sports_dictionnary:
                type = "SPORT"
            print(f"Chunk : ({chunk[0]}, {type})")
            if isinstance(chunk, nl.tree.Tree):
            # Extract words from the chunk
                words = [word for word, pos in chunk.leaves()]
                # Join the words to form a phrase
                phrase = ' '.join(words)
                # Print the phrase and the chunk label
                print(f"\tSpecial case({phrase}, {chunk.label()})")
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traitement de texte par NLP")
    parser.add_argument("--text",help="Texte à traiter")
    parser.add_argument("--file",help="Fichier texte à traiter")

    args = parser.parse_args()
    
    text = args.text
    file = args.file
    update_packages()
    if os.path.exists("./nltk_data/stanford-postagger-full-2020-11-17") and (text is not None or file is not None):
        standFordJarTagger = "./nltk_data/stanford-postagger-full-2020-11-17/stanford-postagger.jar"
        standfordFrenchTaggerFile = "./nltk_data/stanford-postagger-full-2020-11-17/models/french-ud.tagger"
        taggerModel = StanfordPOSTagger(standfordFrenchTaggerFile,standFordJarTagger,encoding='utf8')
        if text is not None:
            print(nl.tokenize.word_tokenize(text,language="french",))
            process_sentences(text)
        elif file is not None:
            if os.path.exists(file) and os.path.isfile(file):
                file_content : np.ndarray = np.asarray([])
                file_content_string = ""
                with open(file) as f:
                   for line in f.readlines():
                       if line is not "" and line is not "\n":
                        file_content = np.append(file_content,line.strip())
                        file_content_string+=line.strip()+". "
                  
                print(f"File Content : {file_content}")
                print(f"File String : {file_content_string}")
                process_sentences(file_content_string)
                
              
                    
        else:
            print(args)
    else:
        print("Usage : --text <text à traiter>")
        