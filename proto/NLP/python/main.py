import argparse
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
import nltk as nl

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
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traitement de texte par NLP")
    parser.add_argument("--text",help="Texte à traiter")
    args = parser.parse_args()
    
    text = args.text
    update_packages()
    if(os.path.exists("./nltk_data/stanford-postagger-full-2020-11-17") and text is not None):
        standFordJarTagger = "./nltk_data/stanford-postagger-full-2020-11-17/stanford-postagger.jar"
        standfordFrenchTaggerFile = "./nltk_data/stanford-postagger-full-2020-11-17/models/french-ud.tagger"
        taggerModel = StanfordPOSTagger(standfordFrenchTaggerFile,standFordJarTagger,encoding='utf8')
        if text is not None:
            print(nl.tokenize.word_tokenize(text,language="french",))
            for sent in nl.sent_tokenize(text):
                print(f"POS tagging : {taggerModel.tag(nl.word_tokenize(sent,language='french'))}")
                print(f"CHUNKING : {nl.ne_chunk(taggerModel.tag(nl.word_tokenize(sent,language='french')))}")
                # Besoin de capter précisément ce que le chunking ne fait pas c
                for chunk in nl.ne_chunk(taggerModel.tag(nl.word_tokenize(sent,language="french"))):
                    print(f"Chunk : {chunk}")
        else:
            print(args)
    else:
        print("Usage : --text <text à traiter>")
        