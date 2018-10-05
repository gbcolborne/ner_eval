/**
 * This software is released under the University of Illinois/Research and Academic Use License. See
 * the LICENSE file in the root folder for details. Copyright (c) 2016
 *
 * Developed by: The Cognitive Computation Group University of Illinois at Urbana-Champaign
 * http://cogcomp.cs.illinois.edu/
 */
package edu.illinois.cs.cogcomp.ner.LbjTagger;

import edu.illinois.cs.cogcomp.core.datastructures.ViewNames;
import edu.illinois.cs.cogcomp.lbjava.parse.LinkedVector;
import edu.illinois.cs.cogcomp.ner.ExpressiveFeatures.ExpressiveFeaturesAnnotator;
import edu.illinois.cs.cogcomp.ner.IO.OutFile;
import edu.illinois.cs.cogcomp.ner.InferenceMethods.Decoder;
import edu.illinois.cs.cogcomp.ner.LbjFeatures.NETaggerLevel1;
import edu.illinois.cs.cogcomp.ner.LbjFeatures.NETaggerLevel2;
import edu.illinois.cs.cogcomp.ner.ParsingProcessingData.PlainTextReader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.ArrayList;
import java.util.Date;
import java.util.Vector;

public class NETagBIO {
    private static final String NAME = NETagBIO.class.getCanonicalName();

    private static NETaggerLevel1 tagger1 = null;
    private static NETaggerLevel2 tagger2 = null;

    private static Logger logger = LoggerFactory.getLogger(NETagBIO.class);

    /**
     * assumes ParametersForLbjCode has been initialized
     */
    public static void init() {
        String modelFile = ParametersForLbjCode.currentParameters.pathToModelFile;
        tagger1 = (NETaggerLevel1) ParametersForLbjCode.currentParameters.taggerLevel1;
        tagger2 = (NETaggerLevel2) ParametersForLbjCode.currentParameters.taggerLevel2;
    }

    /**
     * Does this assume that {@link #init()} has been called already?
     *
     * @param inputPath
     * @param outputPath
     * @throws Exception
     */
    public static void tagData(String inputPath, String outputPath) throws Exception {
        File f = new File(inputPath);
        Vector<String> inFiles = new Vector<>();
        Vector<String> outFiles = new Vector<>();
        if (f.isDirectory()) {
            String[] files = f.list();
            for (String file : files)
                if (!file.startsWith(".")) {
                    inFiles.addElement(inputPath + File.separator + file);
                    outFiles.addElement(outputPath + File.separator + file);
                }
        } else {
            inFiles.addElement(inputPath);
            outFiles.addElement(outputPath);
        }

        for (int fileId = 0; fileId < inFiles.size(); fileId++) {
            logger.debug("Tagging file: " + inFiles.elementAt(fileId));
	    Data data = new Data(inFiles.elementAt(fileId), inFiles.elementAt(fileId), "-c", 
				 new String[] {}, new String[] {});
            String tagged = tagData(data, tagger1, tagger2);
            OutFile out = new OutFile(outFiles.elementAt(fileId));
            out.print(tagged);
            out.close();
        }
    }

    public static String tagData(Data data) throws Exception {
        return tagData(data, tagger1, tagger2);
    }

    public static String tagData(Data data, NETaggerLevel1 tagger1, NETaggerLevel2 tagger2)
            throws Exception {
        ExpressiveFeaturesAnnotator.annotate(data);
        Decoder.annotateDataBIO(data, tagger1, tagger2);

        StringBuffer res = new StringBuffer();
        for (int docid = 0; docid < data.documents.size(); docid++) {
            ArrayList<LinkedVector> sentences = data.documents.get(docid).sentences;
            for (LinkedVector vector : sentences) {
                boolean open = false;
		String[] goldLabels = new String[vector.size()];
                String[] predictions = new String[vector.size()];
                String[] words = new String[vector.size()];
                for (int j = 0; j < vector.size(); j++) {
                    words[j] = ((NEWord) vector.get(j)).form;
		    goldLabels[j] = ((NEWord) vector.get(j)).neLabel;
                    predictions[j] = ((NEWord) vector.get(j)).neTypeLevel2;
                }
		if (vector.size() == 1 && words[0].equals("-DOCSTART-")) {
		    res.append(words[0] + "\n");
		}
		else {
		    for (int j = 0; j < vector.size(); j++) {
			res.append(words[j] + " " + goldLabels[j] + " " + predictions[j] + "\n");
		    }
		}
		res.append("\n");
            }
        }
        return res.toString();
    }
}
