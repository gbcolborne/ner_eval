import spacy, argparse
#import thinc.neural.gpu_ops
from spacy.tokens import Doc

doc = """Test SpaCy. Apply its NER model to pre-tokenized text and get
the predicted labels."""

parser = argparse.ArgumentParser(description=doc)
args = parser.parse_args()

# Load a model (a Language object)
model = "en_core_web_md"
print("Loading {}...".format(model))
nlp = spacy.load(model)

# Basic usage. See https://spacy.io/usage/spacy-101.
print("Processing text...")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion.")
print("\nTokens (with POS tags and dependencies):")
for token in doc:
    print(token.text, token.pos_, token.dep_)
print("\nEntities:")
for ent in doc.ents:
    print(ent.text, ent.label_)

# The model contains a tokenizer that converts a string to a Doc, and
# an ordered series of components that add annotations to that doc.
print("\nPipeline:")
for (name, proc) in nlp.pipeline:
    print("- {}".format(name))

# Let's remove the tagger and parser, which we don't need to do NER.
# Note: you can do this when loading the model, using the "disable"
# keyword -- see https://spacy.io/usage/processing-pipelines.
print("\nRemoving tagger and parser...")
_ = nlp.remove_pipe("tagger")
_ = nlp.remove_pipe("parser")
print("\nPipeline:")
for (name, proc) in nlp.pipeline:
    print("- {}".format(name))

# To apply the NER pipeline to some pre-tokenized text, we first have
# to create a Doc from a list of tokens. See
# https://spacy.io/usage/linguistic-features#own-annotations. # Note:
# If spaces aren't provided, each token is assumed to be followed by a
# space.
print("\nMaking doc from pre-tokenized text...")
words = ["Apple", "is", "looking", "at", "buying", "U.K.", "startup", "for", "$", "1", "billion", "."]
spaces = [True, True, True, True, True, True, True, True, False, True, True, True] 
doc = Doc(nlp.vocab, words=words, spaces=spaces)
print([(t.text, t.text_with_ws, t.whitespace_) for t in doc])

# Now apply the pipeline (which now only contains the NER component)
# to this doc. Another method would be to retrieve the component (or
# "pipe") by calling nlp.get_pipe("ner") and applying this pipe to the
# Doc.
print("\nApplying NER to pretokenized text...")
for (name, proc) in nlp.pipeline:
    doc = proc(doc)
print("\nEntities:")
for ent in doc.ents:
    print(ent.text, ent.label_)


# Show BIO-2 tags of tokens
print("\nBIO-2 tags:")
for token in doc:
    if token.ent_iob_ == "O":
        print("{} O".format(token.text))
    else:
        print("{} {}-{}".format(token.text, token.ent_iob_, token.ent_type_))
    
