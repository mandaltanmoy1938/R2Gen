# exp setup
import spacy
from negspacy.termsets import termset
from negspacy.negation import Negex


class NegationDetection(object):
    def __init__(self, args):
        self.negex = Negex
        self.args = args
        self.nlp_model_sci = spacy.load("en_core_sci_sm")
        self.nlp_model_bc5cdr = spacy.load("en_ner_bc5cdr_md")
        self.clinical_termset = termset("en_clinical")
        self.ann_neg = dict(id="", ann=dict(sentence="", sci=list(dict()), bc5cdr=list(dict())))
        # self.entities = ["DISEASE", "TEST", "TREATMENT", "NEG_ENTITY"]
        self.clinical_termset.add_patterns({
            "pseudo_negations": ["normal", "stable"],
            "preceding_negations": ["no", "free of"],
            "following_negations": ["normal", "stable"],
        })
        self.nlp_model_sci.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.nlp_model_bc5cdr.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})

    def get_doc_object(self, report):
        self.ann_neg["id"] = report["id"]
        # print("id:", report["id"])
        for sentence in report["report"].split('.'):
            # lem_sentence = self.lemmatize(sentence, self.nlp0)
            sentence = sentence.strip()
            if not sentence:
                continue
            self.ann_neg["ann"]["sentence"] = sentence
            self.print_negation(self.nlp_model_sci(sentence), "sci")
            self.print_negation(self.nlp_model_bc5cdr(sentence), "bc5cdr")
        print(self.ann_neg)

    def lemmatize(self, report, nlp_model):
        doc = nlp_model(report)
        lemNote = [wd.lemma_ for wd in doc]
        return " ".join(lemNote)

    def print_negation(self, doc, model):
        for entity in doc.ents:
            self.ann_neg["ann"][model].append(
                {"text": entity.text, "negative": entity._.negex, "label": entity.label_})
            # print(model, ":", entity.text, entity._.negex, entity.label_)
