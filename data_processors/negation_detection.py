# exp setup
import spacy
from negspacy.termsets import termset
from negspacy.negation import Negex


class NegationDetection(object):
    def __init__(self, args):
        self.args = args
        self.nlp_model_sci = spacy.load("en_core_sci_sm")
        self.nlp_model_bc5cdr = spacy.load("en_ner_bc5cdr_md")
        self.clinical_termset = termset("en_clinical")
        # self.entities = ["DISEASE", "TEST", "TREATMENT", "NEG_ENTITY"]
        self.clinical_termset.add_patterns({
            "pseudo_negations": ["normal", "stable"],
            "preceding_negations": ["no", "free of"],
            "following_negations": ["normal", "stable"],
        })
        self.nlp_model_sci.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.nlp_model_bc5cdr.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})

    def get_doc_object(self, report):
        print("id:", report["id"])
        for sentence in report["report"].split('.'):
            # lem_sentence = self.lemmatize(sentence, self.nlp0)
            sentence = sentence.strip()
            if not sentence:
                continue
            print("sent: ", sentence)
            self.print_negation(self.nlp_model_sci(sentence), "sci")
            self.print_negation(self.nlp_model_bc5cdr(sentence), "bc5cdr")

    def lemmatize(self, report, nlp_model):
        doc = nlp_model(report)
        lemNote = [wd.lemma_ for wd in doc]
        return " ".join(lemNote)

    def print_negation(self, doc, model):
        for entity in doc.ents:
            print(model, ":", entity.text, entity._.negex, entity.label_)
