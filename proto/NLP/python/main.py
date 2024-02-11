import argparse
import nltk as nl
import os

def update_packages():
    nl.data.path.append(os.getcwd()+"/nltk_data")
    os.makedirs("nltk_data",exist_ok=True)
    if(not os.path.exists("./nltk_data/tokenizers/punkt")):
        nl.download("punkt",download_dir="./nltk_data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traitement de texte par NLP")
    parser.add_argument("--text",help="Texte à traiter")
    args = parser.parse_args()
    
    text = args.text
    update_packages()
    if text is not None:
        print(nl.tokenize.word_tokenize(text,language="french",))
    else:
        print(args)
        