import sys
import matplotlib
# backend use of matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv


def make_plots(log_name, yaxis='percentage'):
    n_plots = 0
    data = None
    with open(log_name, 'r') as f:
        data = csv.reader(f)
        data = [line for line in data]
    columns_names = data[0]
    n_plots = len(columns_names) - 1
    time_axis = []
    columns_data = [[] for i in range(n_plots)]
    for i in range(1, len(data)):
        line = data[i]
        time_axis.append(float(line[0]))
        for i in range(1, len(line)):
            columns_data[i-1].append(float(line[i]))
    for i in range(n_plots):
        plt.plot(time_axis, columns_data[i])
        if yaxis == 'percentage':
            plt.axis([0, time_axis[-1], 0, 100])
        plt.xlabel(columns_names[0])
        plt.ylabel(columns_names[i+1])
        # plt.title(...)
        plt.savefig("{}_{}_plot.png".format(log_name, columns_names[i+1]))
        plt.close()


def make_parametric_plots(outfile_prefix, parameter_name, parametric_data, fields, legend_position, axis_list=None):
    n_cols = len(fields)
    for j in range(1, n_cols):
        doit=0
        for i in parametric_data.keys():
            rows = parametric_data[i]
            time_axis = [row[0] for row in rows]
            yaxis = [row[j] for row in rows]
            plt.plot(time_axis, yaxis, label="{} {}".format(i, parameter_name))
            if doit==0:
                plt.xlabel(fields[0])
                plt.ylabel(fields[j])
                if axis_list is not None:
                    plt.axis(axis_list[j-1])
                doit=1
        plt.legend(loc=legend_position)
        plt.savefig("{}_{}_plot.png".format(outfile_prefix, fields[j]))
        plt.close()
            

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Usage: python make_plots.py <outfile_prefix> <file_name_1> ... <file_name_N>")
        print("Files must be of the format:")
        print("<Time column> <Data column1> ... <Data columnN>")
    else:
        fields = ['Number of TX', 'Mean TPS', 'Mean total bytes of node traffic']
        xlow, xhigh, ylow = 0, 10000, 0
        yhigh_1, yhigh_2 = 3, 7000000
        axis_list = [[xlow, xhigh, ylow, yhigh_1], [xlow, xhigh, ylow, yhigh_2]]
        outfile_prefix = sys.argv[1]
        files = [sys.argv[i] for i in range(2, len(sys.argv))]
        data = {}
        keys = [2**(i-1) for i in range(2, len(sys.argv))]
        j = 0
        for file in files:
            with open(file, 'r') as f:
                rows = csv.reader(f)
                rows = [line for line in rows]
            data[keys[j]] = [rows[i] for i in range(1, len(rows))]
            j += 1
        make_parametric_plots(outfile_prefix, 'Peer(s)', data, fields, 'lower right', axis_list)
        

