import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme(style="ticks", color_codes=True)


class Plot(object):
    def __init__(self, args, analyze):
        self.is_save_plot = args.is_save_plot
        self.analyze = analyze
        self.normal_color = "#64B5CD"
        self.abnormal_color = "#4C72B0"
        self.indexed_color = "#CCB974"
        self.no_index_color = "#DD8452"
        self.mesh_color = "#8172B3"
        self.no_mesh_color = "#DA8BC3"
        self.train_color = "#64B5CD"
        self.val_color = "#CCB974"
        self.test_color = "#DA8BC3"
        self.dataset, self.dataset_t = self.get_info_dict()

    def populate_analyze(self):
        self.analyze.get_number_of_normal()
        self.analyze.get_number_of_no_index()
        self.analyze.get_number_of_empty_mesh_asc()
        self.analyze.get_samples_size()

    def get_info_dict(self):
        self.populate_analyze()
        data_dict = list(dict())
        data_dict.append({"split": "train", "normal": self.analyze.train_number_of_normal,
                          "no_index": self.analyze.train_number_of_no_index,
                          "no_mesh": self.analyze.train_number_of_empty_mesh,
                          "sample_size": self.analyze.train_size, "t_ratio": 1})
        data_dict.append({"split": "val", "normal": self.analyze.val_number_of_normal,
                          "no_index": self.analyze.val_number_of_no_index,
                          "no_mesh": self.analyze.val_number_of_empty_mesh,
                          "sample_size": self.analyze.val_size, "t_ratio": 1})
        data_dict.append({"split": "test", "normal": self.analyze.test_number_of_normal,
                          "no_index": self.analyze.test_number_of_no_index,
                          "no_mesh": self.analyze.test_number_of_empty_mesh,
                          "sample_size": self.analyze.test_size, "t_ratio": 1})

        dataset = pd.DataFrame(data_dict)
        dataset.loc[3] = pd.Series(
            ["total", dataset["normal"].sum(), dataset["no_index"].sum(), dataset["no_mesh"].sum(),
             dataset["sample_size"].sum(), 1], index=data_dict[0].keys())
        dataset["normal_ratio"] = dataset["normal"] / dataset["sample_size"]
        dataset["no_index_ratio"] = dataset["no_index"] / dataset["sample_size"]
        dataset["no_mesh_ratio"] = dataset["no_mesh"] / dataset["sample_size"]
        dataset["abnormal"] = dataset["sample_size"] - dataset["normal"]
        dataset["indexed"] = dataset["sample_size"] - dataset["no_index"]
        dataset["meshed"] = dataset["sample_size"] - dataset["no_mesh"]
        dataset["abnormal_ratio"] = dataset["abnormal"] / dataset["sample_size"]
        dataset["indexed_ratio"] = dataset["indexed"] / dataset["sample_size"]
        dataset["meshed_ratio"] = dataset["meshed"] / dataset["sample_size"]

        dataset_t = dataset.transpose()
        dataset_t.columns = dataset["split"]
        dataset_t = dataset_t.drop(
            index=["split", "t_ratio", "normal_ratio", "no_index_ratio", "no_mesh_ratio", "abnormal_ratio",
                   "indexed_ratio", "meshed_ratio"])
        dataset_t = dataset_t.reindex(['normal', 'abnormal', 'no_index', 'indexed', 'no_mesh', 'meshed', 'sample_size'])
        dataset_t["-test"] = dataset_t["total"] - dataset_t["test"]
        dataset_t["ys"] = dataset_t.index

        return dataset, dataset_t

    def plot_stacked_bar(self, dataset, num, xs, ys, colors, legend_labels, number_of_col_in_legend, plot_name,
                         save_name,
                         custom_bar_value=None, round_to=4, div_factor=1.5, xylabels=["", ""], ha='center'):
        plt.figure(num=num)
        bar_legends = []
        ax = None
        if len(xs) == len(ys) == len(colors) == len(legend_labels):
            for i in range(len(xs)):
                ax = sns.barplot(x=xs[i], y=ys[i], data=dataset, color=colors[i])
                if custom_bar_value is None:
                    ax.bar_label(container=ax.containers[0])
                else:
                    for index, row in enumerate(custom_bar_value["ys"]):
                        ax.text(dataset[xs[i]][index] / div_factor, row,
                                round(dataset[custom_bar_value["value_key"][i]][index], round_to), color='black',
                                ha=ha)
                bar_legends.append(mpatches.Patch(color=colors[i], label=legend_labels[i]))
                ax.set(xlabel=xylabels[0], ylabel=xylabels[1])
                # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
                # ax.set_yticklabels(ax.get_yticklabels(), rotation=45)
        else:
            if len(xs) == 1 and len(ys) == len(colors) == len(legend_labels):
                for i in range(len(ys)):
                    ax = sns.barplot(x=xs[0], y=ys[i], data=dataset, color=colors[i])
                    if custom_bar_value is None:
                        ax.bar_label(container=ax.containers[0])
                    else:
                        for index, row in enumerate(custom_bar_value["ys"]):
                            ax.text(dataset[xs[i]][index] / div_factor, row,
                                    round(dataset[custom_bar_value["value_key"][i]][index], round_to), color='black',
                                    ha=ha)
                    bar_legends.append(mpatches.Patch(color=colors[i], label=legend_labels[i]))
                    ax.set(xlabel=xylabels[0], ylabel=xylabels[1])
                    # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
                    # ax.set_yticklabels(ax.get_yticklabels(), rotation=45)
            if len(ys) == 1 and len(xs) == len(colors) == len(legend_labels):
                for i in range(len(xs)):
                    ax = sns.barplot(x=xs[i], y=ys[0], data=dataset, color=colors[i])
                    if custom_bar_value is None:
                        ax.bar_label(container=ax.containers[0])
                    else:
                        for index, row in enumerate(custom_bar_value["ys"]):
                            ax.text(dataset[xs[i]][index] / div_factor, row,
                                    round(dataset[custom_bar_value["value_key"][i]][index], round_to), color='black',
                                    ha=ha)
                    bar_legends.append(mpatches.Patch(color=colors[i], label=legend_labels[i]))
                    ax.set(xlabel=xylabels[0], ylabel=xylabels[1])
                    # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
                    # ax.set_yticklabels(ax.get_yticklabels(), rotation=45)
        plt.legend(loc='upper right', bbox_to_anchor=(1.01, 1.11),
                   ncol=number_of_col_in_legend, fancybox=True, shadow=True, handles=bar_legends)
        plt.title(plot_name, pad=28)
        if self.is_save_plot:
            plt.savefig("plot_assets/" + save_name.lower().replace(" ", "_") + ".png")
