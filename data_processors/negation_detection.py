# exp setup
import pandas as pd
import spacy
from negspacy.negation import Negex
from negspacy.termsets import termset


class NegationDetection(object):
    def __init__(self, args, tokenizer):
        self.negex = Negex
        self.args = args
        self.tokenizer = tokenizer
        self.nlp_model_sci = spacy.load("en_core_sci_sm")
        self.nlp_model_bc5cdr = spacy.load("en_ner_bc5cdr_md")
        self.clinical_termset = termset("en_clinical")

        # self.entities = ["DISEASE", "TEST", "TREATMENT", "NEG_ENTITY"]
        self.clinical_termset.add_patterns({
            # "pseudo_negations": ["within normal limits", "stable"],
            "preceding_negations": ["no", "free of", "normal"],
            "following_negations": ["clear", "intact", "normal", "stable"],
        })
        self.nlp_model_sci.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.nlp_model_bc5cdr.add_pipe("negex", config={"neg_termset": self.clinical_termset.get_patterns()})
        self.negex_ann = self.populate_ann_neg()

    def populate_ann_neg(self):
        negex_ann = list()
        for split, split_sample in self.tokenizer.data_processor.iu_mesh_impression_split.items():
            break_count = 0
            for r_id, sample in split_sample.items():
                if split == "train" and self.args.train_sample > 0:
                    if break_count == self.args.train_sample:
                        break
                if split == "val" and self.args.val_sample > 0:
                    if break_count == self.args.val_sample:
                        break
                if split == "test" and self.args.test_sample > 0:
                    if break_count == self.args.test_sample:
                        break
                if self.args.val_test_partial_data == 1 and sample["iu_mesh"] != "normal":
                    continue

                for sentence in self.tokenizer.clean_report_iu_xray(sample["report"]).split('.'):
                    # lem_sentence = self.lemmatize(sentence, self.nlp0)
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    model_entity_dict = dict(sci=list(dict()), bc5cdr=list(dict()))
                    model_entity_dict = self.get_negation(self.nlp_model_sci(sentence), "sci", model_entity_dict)
                    model_entity_dict = self.get_negation(self.nlp_model_bc5cdr(sentence), "bc5cdr", model_entity_dict)

                    if len(model_entity_dict["bc5cdr"]) > 0:
                        for bc5cdr_en_dict in model_entity_dict["bc5cdr"]:
                            negex_ann.append(
                                {"id": sample["id"], "sentence": sentence, "model": "bc5cdr",
                                 "text": bc5cdr_en_dict["text"], "negex": bc5cdr_en_dict["negex"],
                                 "label": bc5cdr_en_dict["label"]})

                            for sci_en_dict in model_entity_dict["sci"]:
                                if bc5cdr_en_dict["text"] not in sci_en_dict["text"]:
                                    negex_ann.append(
                                        {"id": sample["id"], "sentence": sentence, "model": "sci",
                                         "text": sci_en_dict["text"], "negex": sci_en_dict["negex"],
                                         "label": sci_en_dict["label"]})
                    else:
                        for sci_en_dict in model_entity_dict["sci"]:
                            negex_ann.append(
                                {"id": sample["id"], "sentence": sentence, "model": "sci",
                                 "text": sci_en_dict["text"], "negex": sci_en_dict["negex"],
                                 "label": sci_en_dict["label"]})
                break_count += 1
        return negex_ann

    def to_csv(self):
        pd.DataFrame(self.negex_ann).to_csv('data/iu_xray//kaggle/negex_ann.csv', encoding='utf-8', index=False)

    def lemmatize(self, report, nlp_model):
        doc = nlp_model(report)
        lemNote = [wd.lemma_ for wd in doc]
        return " ".join(lemNote)

    def get_negation(self, doc, model, ann_dict):
        for entity in doc.ents:
            ann_dict[model].append({"text": entity.text, "negex": entity._.negex, "label": entity.label_})
        return ann_dict
