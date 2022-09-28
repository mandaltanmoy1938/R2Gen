# exp setup
import spacy
import pandas as pd
from negspacy.termsets import termset
from negspacy.negation import Negex


class NegationDetection(object):
    def __init__(self, args):
        self.negex = Negex
        self.args = args
        self.nlp_model_sci = spacy.load("en_core_sci_sm")
        self.nlp_model_bc5cdr = spacy.load("en_ner_bc5cdr_md")
        self.clinical_termset = termset("en_clinical")
        self.ann_neg = dict(id="", neg_sents=list())
        # self.entities = ["DISEASE", "TEST", "TREATMENT", "NEG_ENTITY"]
        self.clinical_termset.add_patterns({
            "pseudo_negations": ["normal", "stable"],
            "preceding_negations": ["no", "free of"],
            "following_negations": ["normal", "stable"],
        })
        self.nlp_model_sci.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.nlp_model_bc5cdr.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})

    def populate_ann_neg(self, report):
        self.ann_neg["id"] = report["id"]
        # print("id:", report["id"])
        for sentence in report["report"].split('.'):
            # lem_sentence = self.lemmatize(sentence, self.nlp0)
            sentence = sentence.strip()
            if not sentence:
                continue
            neg_sent = dict(sentence=sentence, sci=list(dict()), bc5cdr=list(dict()))

            neg_sent = self.get_negation(self.nlp_model_sci(sentence), "sci", neg_sent)
            neg_sent = self.get_negation(self.nlp_model_bc5cdr(sentence), "bc5cdr", neg_sent)
            self.ann_neg["neg_sents"].append(neg_sent)

    def to_csv(self):
        ann_neg = pd.DataFrame(self.ann_neg)
        ann_neg.to_csv('data/iu_xray//kaggle/ann_neg.csv', encoding='utf-8', index=False)

    def lemmatize(self, report, nlp_model):
        doc = nlp_model(report)
        lemNote = [wd.lemma_ for wd in doc]
        return " ".join(lemNote)

    def get_negation(self, doc, model, neg_sent):
        for entity in doc.ents:
            neg_sent[model].append({"text": entity.text, "negative": entity._.negex, "label": entity.label_})
        return neg_sent
