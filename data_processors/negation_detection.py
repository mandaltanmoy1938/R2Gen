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
        self.ann_neg = list()
        # self.entities = ["DISEASE", "TEST", "TREATMENT", "NEG_ENTITY"]
        self.clinical_termset.add_patterns({
            "pseudo_negations": ["normal", "stable"],
            "preceding_negations": ["no", "free of"],
            "following_negations": ["normal", "stable"],
        })
        self.nlp_model_sci.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.nlp_model_bc5cdr.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})

    def populate_ann_neg(self, report):
        for sentence in report["report"].split('.'):
            # lem_sentence = self.lemmatize(sentence, self.nlp0)
            sentence = sentence.strip()
            if not sentence:
                continue
            model_entity_dict = dict(sci=list(dict()), bc5cdr=list(dict()))
            model_entity_dict = self.get_negation(self.nlp_model_sci(sentence), "sci", model_entity_dict)
            model_entity_dict = self.get_negation(self.nlp_model_bc5cdr(sentence), "bc5cdr", model_entity_dict)

            for bc5cdr_en_dict in model_entity_dict["bc5cdr"]:
                self.ann_neg.append(
                    {"id": report["id"], "sentence": sentence, "model": "bc5cdr", "text": bc5cdr_en_dict["text"],
                     "negex": bc5cdr_en_dict["negex"], "label": bc5cdr_en_dict["label"]})
            for sci_en_dict in model_entity_dict["sci"]:
                # if bc5cdr_en_dict["text"] not in sci_en_dict["text"]:
                self.ann_neg.append(
                    {"id": report["id"], "sentence": sentence, "model": "sci", "text": sci_en_dict["text"],
                     "negex": sci_en_dict["negex"], "label": sci_en_dict["label"]})

    def to_csv(self):
        ann_neg = pd.DataFrame(self.ann_neg)
        ann_neg.to_csv('data/iu_xray//kaggle/ann_neg.csv', encoding='utf-8', index=True)

    def lemmatize(self, report, nlp_model):
        doc = nlp_model(report)
        lemNote = [wd.lemma_ for wd in doc]
        return " ".join(lemNote)

    def get_negation(self, doc, model, ann_dict):
        for entity in doc.ents:
            ann_dict[model].append({"text": entity.text, "negex": entity._.negex, "label": entity.label_})
        return ann_dict
