# exp setup
import csv
import json
import os

from torch.utils.data import random_split

from analytics.analyze import Analyze


class DataProcessor(object):
    def __init__(self, args):
        self.r2gen_ann_path = args.ann_path
        self.kaggle_iu_reports_path = args.kaggle_iu_reports_path
        self.iu_mesh_impression_path_split = args.iu_mesh_impression_path.replace(".json", "_split.json")
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
        self.analyze = Analyze(args)

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
                                    seq_mesh_text = ""
                                    seq_attr_text = ""
                                    if ',' in mesh_attr[0]:
                                        for ma in mesh_attr[0].split(','):
                                            seq_mesh_text += " <mesh:{}>".format(ma.strip().replace(' ', '_'))
                                    else:
                                        seq_mesh_text = " <mesh:{}>".format(mesh_attr[0].strip().replace(' ', '_'))
                                    mesh_text += seq_mesh_text

                                    if len(mesh_attr) == 2:
                                        seq_attr_text = " <attr:{}>".format(mesh_attr[1].strip().replace(' ', '_'))
                                    elif len(mesh_attr) > 2:
                                        for i in range(1, len(mesh_attr)):
                                            seq_attr_text += " <attr:{}>".format(mesh_attr[i].strip().replace(' ', '_'))
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
        if not os.path.exists(self.iu_mesh_impression_path_split):
            os.mknod(self.iu_mesh_impression_path_split)
        json.dump(matched_split, open(self.iu_mesh_impression_path_split, 'w'))
        if not os.path.exists(self.iu_mesh_impression_path):
            os.mknod(self.iu_mesh_impression_path)
        json.dump(matched, open(self.iu_mesh_impression_path, 'w'))
        return matched_split, matched

    def get_reports_by_exp(self, exp, split, r2gen_id, report):
        if split == 'train' and 4 < exp < 9:
            report += " <sep> " + self.iu_mesh_impression_split[split][r2gen_id]['impression']

        if split == 'train':
            if exp == 2:
                return report + " <sep>" + self.iu_mesh_impression_split[split][r2gen_id]['mesh']
            elif exp == 3:
                return report + " <sep>" + self.iu_mesh_impression_split[split][r2gen_id]['attr']
            elif exp == 4:
                return report + " <sep>" + self.iu_mesh_impression_split[split][r2gen_id]['mesh_attr']
            elif exp == 6:
                return report + self.iu_mesh_impression_split[split][r2gen_id]['mesh']
            elif exp == 7:
                return report + self.iu_mesh_impression_split[split][r2gen_id]['attr']
            elif exp == 8:
                return report + self.iu_mesh_impression_split[split][r2gen_id]['mesh_attr']
        return report

    def split_dataset(self):
        dataset_keys = list(self.iu_mesh_impression.keys())
        train_size = int(0.7 * len(dataset_keys))  # 2068
        test_size = int(0.2 * len(dataset_keys))  # 591
        val_size = len(dataset_keys) - train_size - test_size  # 296

        train_set, val_set, test_set = random_split(dataset_keys, [train_size, val_size, test_size])
        split_data = dict(train={}, val={}, test={})
        split_data["train"] = {k: self.iu_mesh_impression[k] for k in train_set}
        split_data["val"] = {k: self.iu_mesh_impression[k] for k in val_set}
        split_data["test"] = {k: self.iu_mesh_impression[k] for k in test_set}

        if not os.path.exists(self.iu_mesh_impression_path_split):
            os.mknod(self.iu_mesh_impression_path_split)
        json.dump(split_data, open(self.iu_mesh_impression_path_split, 'w'))

        split_data = dict(train=[], val=[], test=[])
        split_data["train"] = [self.iu_mesh_impression[k] for k in train_set]
        split_data["val"] = [self.iu_mesh_impression[k] for k in val_set]
        split_data["test"] = [self.iu_mesh_impression[k] for k in test_set]

        self.r2gen_ann_path = self.r2gen_ann_path.replace("r2gen", "kaggle")
        if not os.path.exists(self.r2gen_ann_path):
            os.mknod(self.r2gen_ann_path)
        json.dump(split_data, open(self.r2gen_ann_path, 'w'))

    def validate_association(self):
        self.analyze.get_number_of_normal()
        self.analyze.get_number_of_no_index()
        self.analyze.get_number_of_empty_mesh_asc()

        return (
                self.analyze.total_number_of_empty_mesh == self.analyze.total_number_of_normal + self.analyze.total_number_of_no_index
                and self.analyze.train_number_of_empty_mesh == self.analyze.train_number_of_normal + self.analyze.train_number_of_no_index
                and self.analyze.val_number_of_empty_mesh == self.analyze.val_number_of_normal + self.analyze.val_number_of_no_index
                and self.analyze.test_number_of_empty_mesh == self.analyze.test_number_of_normal + self.analyze.test_number_of_no_index)
    ############################################