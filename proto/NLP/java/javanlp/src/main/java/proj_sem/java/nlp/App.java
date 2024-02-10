package proj_sem.java.nlp;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Arrays;
import java.util.stream.Stream;

import opennlp.tools.namefind.TokenNameFinderModel;
import opennlp.tools.tokenize.Tokenizer;
import opennlp.tools.tokenize.TokenizerME;
import opennlp.tools.tokenize.TokenizerModel;

/**
 * Documentation OpenNLP
 * https://opennlp.apache.org/docs/2.3.2/manual/opennlp.html
 * 
 * Modèles utilisés par OpenNLP
 * https://opennlp.sourceforge.net/models-1.5/ 
 * 
 * NER Training w/OpenNLP
 * https://medium.com/analytics-vidhya/named-entity-recognition-in-java-using-open-nlp-4dc7cfc629b4 
 * 
 */
public class App {

    private static String[] tokenizer(String sentence_to_nlp){
        try (InputStream modelIn = new FileInputStream("en-token.bin")) {
            TokenizerModel model = new TokenizerModel(modelIn);
            Tokenizer tokenizer = new TokenizerME(model);
            String tokens[] = tokenizer.tokenize(sentence_to_nlp);
            return tokens;
        }catch (Exception e){
             return new String[0];
        }
    }

    // private static String[] named_entity_reco(String sentence_to_nlp){
    //     try (InputStream modelIn = new FileInputStream("en-token.bin")) {
    //         TokenNameFinderModel  model = new TokenNameFinderModel(modelIn);
    //         Tokenizer tokenizer = new TokenizerME(model);
    //         String tokens[] = tokenizer.tokenize(sentence_to_nlp);
    //         return tokens;
    //     }catch (Exception e){
    //          return new String[0];
    //     }
    // }


    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new Exception("Missing arguments");
        } else {
            String sentence_to_nlp = args[1];
            System.out.println(sentence_to_nlp);
            String[] tokens = tokenizer(sentence_to_nlp);
            Stream<String> stream = Arrays.stream(tokens);
            stream.forEach(str -> System.out.println(str));
        }
    }
}
