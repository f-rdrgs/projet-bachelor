package proj_sem.java.nlp;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.util.Arrays;
import java.util.stream.Stream;
import opennlp.tools.tokenize.Tokenizer;
import opennlp.tools.tokenize.TokenizerME;
import opennlp.tools.tokenize.TokenizerModel;

/**
 * Documentation OpenNLP
 * https://opennlp.apache.org/docs/2.3.2/manual/opennlp.html
 * 
 */
public class App {
    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            throw new Exception("Missing arguments");
        } else {
            String sentence_to_nlp = args[1];
            System.out.println(sentence_to_nlp);
            try (InputStream modelIn = new FileInputStream("en-token.bin")) {
                TokenizerModel model = new TokenizerModel(modelIn);
                Tokenizer tokenizer = new TokenizerME(model);
                String tokens[] = tokenizer.tokenize(sentence_to_nlp);
                Stream<String> stream = Arrays.stream(tokens);
                stream.forEach(str -> System.out.println(str));
            }
        }
    }
}
