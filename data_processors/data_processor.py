# exp setup
import csv
import json
import os

from analytics.analyze import Analyze


class DataProcessor(object):
    def __init__(self, args):
        self.args = args
        self.r2gen_ann_path = args.ann_path
        self.kaggle_ann_path = self.r2gen_ann_path.replace("r2gen", "kaggle")
        self.is_new_random_split = args.is_new_random_split
        self.kaggle_iu_reports_path = args.kaggle_iu_reports_path
        self.iu_mesh_impression_path_split = args.iu_mesh_impression_path.replace(".json", "_split.json")
        self.iu_mesh_impression_path_new_split = args.iu_mesh_impression_path.replace(".json", "_new_split.json")
        self.iu_mesh_impression_path = args.iu_mesh_impression_path
        self.create_r2gen_kaggle_association = args.create_r2gen_kaggle_association
        self.iu_mesh_impression_split = dict()
        self.iu_mesh_impression = dict()

        if self.create_r2gen_kaggle_association == 0 and \
                os.path.exists(self.iu_mesh_impression_path_split) and os.path.exists(self.iu_mesh_impression_path):
            self.iu_mesh_impression_split = json.loads(open(self.iu_mesh_impression_path_split, 'r').read())
            self.iu_mesh_impression = json.loads(open(self.iu_mesh_impression_path, 'r').read())
        else:
            self.iu_mesh_impression_split, self.iu_mesh_impression = self.associate_iu_r2gen_kaggle_by_id()
            # self.dump_to_json(self.iu_mesh_impression, self.iu_mesh_impression_path)
            # self.dump_to_json(self.iu_mesh_impression_split, self.iu_mesh_impression_path_split)
        self.analyze = Analyze(args, self.iu_mesh_impression_split)

    def associate_iu_r2gen_kaggle_by_id(self):
        kaggle_iu_reports = csv.reader(open(self.kaggle_iu_reports_path, 'r'))
        r2gen_ann = json.loads(open(self.r2gen_ann_path, 'r').read())
        next(kaggle_iu_reports)
        r2gen_splits_ids_reports = {
            split: [{sample["id"]: sample} for sample in samples]
            for split, samples in r2gen_ann.items()
        }

        kaggle_uids_mesh_impression = {
            line[0]: {"MeSH": line[1], "report": line[6], "impression": line[7]}
            for line in kaggle_iu_reports
        }

        unmatched_split = dict(train={}, val={}, test={})
        matched_split = dict(train={}, val={}, test={})
        unmatched = dict()
        matched = dict()
        for split, samples in r2gen_splits_ids_reports.items():
            for sample in samples:
                for r2gen_id, r2gen_value in sample.items():
                    uid = r2gen_id.split('_')[0].replace("CXR", "")
                    if uid in kaggle_uids_mesh_impression:
                        kaggle_report = kaggle_uids_mesh_impression[uid]["report"]
                        if r2gen_value["report"] == kaggle_report:
                            iu_mesh = kaggle_uids_mesh_impression[uid]["MeSH"]
                            mesh_text = ""
                            attr_text = ""
                            mesh_attr_text = ""
                            for mesh_info in iu_mesh.split(';'):
                                if 'normal' != mesh_info and 'No Indexing' != mesh_info:
                                    mesh_attr = mesh_info.split('/')
                                    seq_attr_text = ""
                                    seq_mesh_text = " <mesh:{}>".format(
                                        mesh_attr[0].strip().replace(', ', '_').replace(' ', '_'))
                                    mesh_text += seq_mesh_text

                                    if len(mesh_attr) == 2:
                                        seq_attr_text = " <attr:{}>".format(
                                            mesh_attr[1].strip().replace(', ', '_').replace(' ', '_'))
                                    elif len(mesh_attr) > 2:
                                        for i in range(1, len(mesh_attr)):
                                            seq_attr_text += " <attr:{}>".format(
                                                mesh_attr[i].strip().replace(', ', '_').replace(' ', '_'))
                                    attr_text += seq_attr_text

                                    mesh_attr_text += "{}{}".format(seq_mesh_text, seq_attr_text)
                            r2gen_value.update({
                                "iu_mesh": iu_mesh, "mesh": mesh_text, "attr": attr_text,
                                "mesh_attr": mesh_attr_text,
                                "impression": kaggle_uids_mesh_impression[uid]["impression"]})
                            matched_split[split][r2gen_id] = r2gen_value
                            matched[r2gen_id] = r2gen_value
                        else:
                            unmatched_split[split][r2gen_id] = {"r2gen_uid": uid, "r2gen_report": r2gen_value,
                                                                "kaggle_report": kaggle_report}
                            unmatched[r2gen_id] = {"r2gen_uid": uid, "r2gen_report": r2gen_value,
                                                   "kaggle_report": kaggle_report}
                    else:
                        unmatched_split[split][r2gen_id] = {"r2gen_uid": uid, "r2gen_report": r2gen_value,
                                                            "kaggle_report": ""}
                        unmatched[r2gen_id] = {"r2gen_uid": uid, "r2gen_report": r2gen_value,
                                               "kaggle_report": ""}
        return matched_split, matched

    def dump_to_json(self, data, path):
        if not os.path.exists(path):
            os.mknod(path)
        json.dump(data, open(path, 'w'))

    def get_reports_by_exp(self, exp, split, r2gen_id, report):
        if 3 < exp < 7:
            report = self.iu_mesh_impression_split[split][r2gen_id]['impression']

        if split == 'train':
            if exp == 2 or exp == 5:
                mesh_attr = " <sep>" + self.iu_mesh_impression_split[split][r2gen_id]['mesh_attr']
                return report + mesh_attr
            elif exp == 3:
                mesh_attr = " <sep>" + self.iu_mesh_impression_split[split][r2gen_id]['auto_generated_ontology_report']
                return report + mesh_attr
            elif exp == 6:
                mesh_attr = " <sep>" + self.iu_mesh_impression_split[split][r2gen_id][
                    'auto_generated_ontology_impression']
                return report + mesh_attr
        return report

    def validate_association(self):
        self.analyze.get_number_of_normal()
        self.analyze.get_number_of_no_index()
        self.analyze.get_number_of_empty_mesh_asc()

        r2gen_ann = json.loads(open(self.r2gen_ann_path, 'r').read())
        flag = True
        if self.is_new_random_split == 0:
            unmatched = list()
            for split, split_data in r2gen_ann.items():
                for sample in split_data:
                    if split in self.iu_mesh_impression_split and sample["id"] in self.iu_mesh_impression_split[split] \
                            and split == sample["split"]:
                        continue
                    else:
                        unmatched.append(sample["id"])
            flag = len(unmatched) == 0

        return (
                self.analyze.total_number_of_empty_mesh == self.analyze.total_number_of_normal + self.analyze.total_number_of_no_index
                and self.analyze.train_number_of_empty_mesh == self.analyze.train_number_of_normal + self.analyze.train_number_of_no_index
                and self.analyze.val_number_of_empty_mesh == self.analyze.val_number_of_normal + self.analyze.val_number_of_no_index
                and self.analyze.test_number_of_empty_mesh == self.analyze.test_number_of_normal + self.analyze.test_number_of_no_index
                and flag)
    ############################################
