# exp setup
import random
import time

from _global import timer
from _global.argument_parser import ArgumentParser
from analytics.experiments_statistics import ExperimentsStatistics
from analytics.analyze import Analyze
from analytics.plot import Plot
from data_processors.data_processor import DataProcessor
from data_processors.negation_detection import NegationDetection
from modules.tokenizers import Tokenizer


def main():
    start_time = time.time()
    # parse arguments
    args = ArgumentParser().args

    # r2gen split
    # args.is_new_random_split = 0
    # to check the old code
    # associate_iu_r2gen_kaggle_by_id(args)
    # mip_j_split = json.loads(open(args.iu_mesh_impression_path, 'r').read())
    # mip_j = {sid: sample for split, split_sample in mip_j_split.items() for sid, sample in split_sample.items()}
    # json.dump(mip_j, open(args.iu_mesh_impression_path.replace("_split", ""), 'w'))
    ######################################

    data_processor = DataProcessor(args)
    print("Is association file valid: ", data_processor.validate_association())
    tokenizer = Tokenizer(args, data_processor)
    # test negation detection
    negation_detection = NegationDetection(args)
    for split, split_sample in data_processor.iu_mesh_impression_split.items():
        # if split == 'train' and args.train_sample > 0:
            # split_sample = random.sample(list(split_sample.values()), args.train_sample)
        # if split == 'val' and args.val_sample > 0:
            # split_sample = random.sample(list(split_sample.values()), args.val_sample)
        # if split == 'test' and args.test_sample > 0:
            # split_sample = random.sample(list(split_sample.values()), args.test_sample)
        split_sample = list(split_sample.values())
        for sample in split_sample[:args.train_sample]:
            negation_detection.get_doc_object(sample)
    #################################################################################
    # exp_stats = ExperimentsStatistics(tokenizer, args.exp)
    # print("exp: ", args.exp, " ", exp_stats.stats)
    #
    # print("######### before split#########")
    # data_processor.analyze.print_normal_percentage()
    # data_processor.analyze.print_no_index_percentage()
    # data_processor.analyze.print_empty_mesh_asc_percentage()
    # print("Is association file valid: ", data_processor.validate_association())
    #
    # plot = Plot(args, data_processor.analyze)
    #
    # number_of_col_in_legend = 3
    # fig_num = 1
    # # Vertical plot
    # # split wise normal
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["normal"],
    #                       colors=[plot.normal_color], legend_labels=['Normal'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Normal by Split",
    #                       save_name="[Split Vertical]Normal")
    #
    # # split wise abnormal
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["abnormal"],
    #                       colors=[plot.abnormal_color], legend_labels=['Abnormal'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Abnormal by Split",
    #                       save_name="[Split Vertical]Abnormal")
    #
    # # split wise no index
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["no_index"],
    #                       colors=[plot.no_index_color], legend_labels=['No Indexing'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="No Indexing by Split",
    #                       save_name="[Split Vertical]No Indexing")
    #
    #
    # # split wise indexed
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["indexed"],
    #                       colors=[plot.indexed_color], legend_labels=['Indexed'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Indexed by Split",
    #                       save_name="[Split Vertical]Indexed")
    #
    # # split wise no mesh
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["no_mesh"],
    #                       colors=[plot.no_mesh_color], legend_labels=['No MeSH'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="No MeSH by Split",
    #                       save_name="[Split Vertical]No MeSH")
    #
    # # split wise meshed
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["split"], ys=["meshed"],
    #                       colors=[plot.mesh_color], legend_labels=['Meshed'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="MeSHed by Split",
    #                       save_name="[Split Vertical]MeSHed")
    #
    # # Horizontal stacked plot
    # # split wise normal
    # fig_num += 1
    # # ['normal', 'abnormal', 'no_index', 'indexed', 'no_mesh', 'meshed', 'sample_size']
    # tmp_datset = plot.dataset_t.drop(index=['abnormal', 'no_index', 'indexed', 'no_mesh', 'meshed', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Normal by split",
    #                       save_name="[Split Horizontal]Normal", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise abnormal
    # fig_num += 1
    # # ['normal', 'abnormal', 'no_index', 'indexed', 'no_mesh', 'meshed', 'sample_size']
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'no_index', 'indexed', 'no_mesh', 'meshed', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Abnormal by split",
    #                       save_name="[Split Horizontal]Abnormal", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise no indexing
    # fig_num += 1
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'abnormal', 'indexed', 'no_mesh', 'meshed', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="No indexing by split",
    #                       save_name="[Split Horizontal]No indexing", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise indexed
    # fig_num += 1
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'abnormal', 'no_index', 'no_mesh', 'meshed', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Indexied by split",
    #                       save_name="[Split Horizontal]Indexed", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise no mesh
    # fig_num += 1
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'abnormal', 'no_index', 'indexed', 'meshed', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="No MeSH by split",
    #                       save_name="[Split Horizontal]No MeSH", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise mesh
    # fig_num += 1
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'abnormal', 'no_index', 'indexed', 'no_mesh', 'sample_size'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="MeSHed by split",
    #                       save_name="[Split Horizontal]MeSHed", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # split wise sample size
    # fig_num += 1
    # tmp_datset = plot.dataset_t.drop(index=['normal', 'abnormal', 'no_index', 'indexed', 'no_mesh', 'meshed'])
    # tmp_datset.index = [*range(len(tmp_datset.index))]
    # plot.plot_stacked_bar(dataset=tmp_datset, num=fig_num,
    #                       xs=["total", "-test", "train"],
    #                       ys=["ys"], colors=[plot.test_color, plot.val_color, plot.train_color],
    #                       legend_labels=['Test', 'Val', 'Train'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Sample size by split",
    #                       save_name="[Split Horizontal]Sample size", div_factor=1.08,
    #                       custom_bar_value={"ys": tmp_datset.index,
    #                                         "value_key": ["test", "val", "train"]})
    #
    # # Horizontal Stacked plot
    # # normal ratio
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["t_ratio", "normal_ratio"], ys=["split"],
    #                       colors=[plot.abnormal_color, plot.normal_color], legend_labels=['Abnormal', 'Normal'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Normal to Abnormal ratio",
    #                       save_name="[Ratio]Normal to Abnormal",
    #                       custom_bar_value={"ys": plot.dataset.head().index,
    #                                         "value_key": ["abnormal_ratio", "normal_ratio"]})
    # # indexed ratio
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["t_ratio", "no_index_ratio"], ys=["split"],
    #                       colors=[plot.indexed_color, plot.no_index_color], legend_labels=['Indexed', 'No Indexing'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Indexed to No Indexing ratio",
    #                       save_name="[Ratio]Indexed to No Indexing", div_factor=3, ha="left",
    #                       custom_bar_value={"ys": plot.dataset.head().index,
    #                                         "value_key": ["indexed_ratio", "no_index_ratio"]})
    # # empty mesh ratio
    # fig_num += 1
    # plot.plot_stacked_bar(dataset=plot.dataset, num=fig_num, xs=["t_ratio", "no_mesh_ratio"], ys=["split"],
    #                       colors=[plot.mesh_color, plot.no_mesh_color], legend_labels=['MeSH', 'No MeSH'],
    #                       number_of_col_in_legend=number_of_col_in_legend, plot_name="Mesh to No MeSH ratio",
    #                       save_name="[Ratio]Mesh to No MeSH",
    #                       custom_bar_value={"ys": plot.dataset.head().index,
    #                                         "value_key": ["meshed_ratio", "no_mesh_ratio"]})

    # # new split
    # args.is_new_random_split = 1
    # data_processor = DataProcessor(args)
    # print("######### after split#########")
    # data_processor.analyze.print_normal_percentage()
    # data_processor.analyze.print_no_index_percentage()
    # data_processor.analyze.print_empty_mesh_asc_percentage()
    # print("Is association file valid: ", data_processor.validate_association())
    #
    # plot = Plot(args, data_processor.analyze)

    # plt.show()
    timer.time_executed(start_time, "R2Gen.Analysis")


# def associate_iu_r2gen_kaggle_by_id(args):
#     kaggle_iu_reports = csv.reader(open(args.kaggle_iu_reports_path, 'r'))
#     r2gen_ann = json.loads(open(args.ann_path, 'r').read())
#     next(kaggle_iu_reports)
#     r2gen_splits_ids_reports = {
#         split: [{sample["id"]: sample["report"]} for sample in samples]
#         for split, samples in r2gen_ann.items()
#     }
#
#     kaggle_uids_mesh_impression = {
#         line[0]: {"MeSH": line[1], "report": line[6], "impression": line[7]}
#         for line in kaggle_iu_reports
#     }
#
#     unmatched = dict(train=[], val=[], test=[])
#     matched = dict(train={}, val={}, test={})
#     for split, samples in r2gen_splits_ids_reports.items():
#         for sample in samples:
#             for r2gen_id, r2gen_report in sample.items():
#                 uid = r2gen_id.split('_')[0].replace("CXR", "")
#                 if uid in kaggle_uids_mesh_impression:
#                     kaggle_report = kaggle_uids_mesh_impression[uid]["report"]
#                     if r2gen_report == kaggle_report:
#                         iu_mesh = kaggle_uids_mesh_impression[uid]["MeSH"]
#                         mesh_text = ""
#                         attr_text = ""
#                         mesh_attr_text = ""
#                         for mesh_info in iu_mesh.split(';'):
#                             if '/' in mesh_info:
#                                 mesh_attr = mesh_info.split('/')
#                                 ma_text = ""
#                                 if ',' in mesh_attr[0]:
#                                     for ma in mesh_attr[0].split(','):
#                                         ma_text += " <mesh:{}>".format(ma.strip().replace(' ', '_'))
#                                 else:
#                                     ma_text = " <mesh:{}>".format(mesh_attr[0].strip().replace(' ', '_'))
#                                 mesh_text += ma_text
#                                 attr_text += " <attr:{}>".format(mesh_attr[1].strip().replace(' ', '_'))
#                                 mesh_attr_text += "{} <attr:{}>".format(ma_text,
#                                                                         mesh_attr[1].strip().replace(' ', '_'))
#                         matched[split][r2gen_id] = {
#                             "iu_mesh": iu_mesh, "mesh": mesh_text, "attr": attr_text,
#                             "mesh_attr": mesh_attr_text,
#                             "impression": kaggle_uids_mesh_impression[uid]["impression"]}
#                         # matched[split].append(matched_info)
#                     else:
#                         unmatched[split][r2gen_id] = {"r2gen_uid": uid, "r2gen_report": r2gen_report,
#                                                       "kaggle_report": kaggle_report}
#                         # unmatched[split].append(unmatched_info)
#                 else:
#                     unmatched_info = {
#                         r2gen_id: {"r2gen_uid": uid, "r2gen_report": r2gen_report, "kaggle_report": ""}}
#                     unmatched[split].append(unmatched_info)
#     if not os.path.exists(args.iu_mesh_impression_path):
#         os.mknod(args.iu_mesh_impression_path)
#     json.dump(matched, open(args.iu_mesh_impression_path, 'w'))
#     return matched

if __name__ == '__main__':
    main()
#############################################################################################
