package proj_sem.java.nlp;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Collections;

import opennlp.tools.namefind.BioCodec;
import opennlp.tools.namefind.NameFinderME;
import opennlp.tools.namefind.NameSampleDataStream;
import opennlp.tools.namefind.TokenNameFinderFactory;
import opennlp.tools.namefind.TokenNameFinderModel;
import opennlp.tools.util.InputStreamFactory;
import opennlp.tools.util.MarkableFileInputStreamFactory;
import opennlp.tools.util.ObjectStream;
import opennlp.tools.util.PlainTextByLineStream;
import opennlp.tools.util.TrainingParameters;

public class NER_train {
    private String data_url;
    private File data_file;

    public void setData_url(String data_url) {
        this.data_url = data_url;
    }

    public String getData_url() {
        return data_url;
    }

    private void load_data_file() {
        File temp_file = new File(this.data_url);
        if (temp_file.exists() && temp_file.isFile())
            data_file = new File(this.data_url);
        else {
            System.err.println("No File was found");
        }
    }

    // https://medium.com/analytics-vidhya/named-entity-recognition-in-java-using-open-nlp-4dc7cfc629b4

    private void train_data(NameSampleDataStream sampleStream, TrainingParameters params) {
        // training the model using TokenNameFinderModel class
        TokenNameFinderModel nameFinderModel = null;
        try {
            nameFinderModel = NameFinderME.train("fr", null, sampleStream,
                    params, TokenNameFinderFactory.create(null, null, Collections.emptyMap(), new BioCodec()));
        } catch (IOException e) {
            e.printStackTrace();
        }
        // saving the model to "ner-custom-model.bin" file
        try {
            File output = new File("ner-custom-model-fr.bin");
            FileOutputStream outputStream = new FileOutputStream(output);
            nameFinderModel.serialize(outputStream);
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void train() {
        if (this.data_file.exists() && this.data_file.isFile()) {
            InputStreamFactory in = null;
            try {
                in = new MarkableFileInputStreamFactory(this.data_file);
                NameSampleDataStream sampleStream = null;
                try {
                    sampleStream = new NameSampleDataStream(
                            new PlainTextByLineStream(in, StandardCharsets.UTF_8));
                    // setting the parameters for training
                    TrainingParameters params = new TrainingParameters();
                    params.put(TrainingParameters.ITERATIONS_PARAM, 70);
                    params.put(TrainingParameters.CUTOFF_PARAM, 1);
                    params.put(TrainingParameters.ALGORITHM_PARAM, "MAXENT");
                    this.train_data(sampleStream, params);
                } catch (IOException e1) {
                    e1.printStackTrace();
                }
            } catch (FileNotFoundException e2) {
                e2.printStackTrace();
            }
           

        } else {
            System.err.println("No file was found");
        }
    }

    public NER_train(String dataset_url) {
        super();
        data_url = dataset_url;
        load_data_file();
    }
}
