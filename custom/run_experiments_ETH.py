import sys
import os
import csv
import time
from tree_N_depth_M_transactions_ETH import run as tx_run
from tree_ETH_with_link_up_and_down import run as faultlink_tx_run
from n_star_topology_ETH import run as star_run

sys.path.append("/home/mininet/Analysis")
from make_plots import make_plots
from make_plots import make_parametric_plots


if __name__=="__main__":
    if len(sys.argv) != 2:
        #print("Usage: sudo python ./{} <maximum_star> <maximum_tree_depth> <maximum_num_tx>".format(sys.argv[0]))
        print("Usage sudo python ./{} <test_case_ID>".format(sys.argv[0]))
        print("Test case ID = 0 means execute all tests")
    else:
        m_star = 40
        m_depth = 3
        tx_range = [250, 500, 1000, 2500, 4000, 5000, 10000]
        test_ID = int(sys.argv[1])
        if test_ID in [0, 1]:
            if m_star < 5:
                m_star = 5
            for i in range(5, m_star+1, 5):
                os.system("sudo mn -c")
                star_run(i)
                # wait for nodes to quit
                time.sleep(100)
        if m_depth < 1:
            m_depth = 1
        fields = ['Number of TX', 'Mean TPS', 'Mean total bytes of node traffic']
        data = {}
        faultlink_data = {}
        unique = time.strftime("%d_%m_%Y_%H:%M", time.localtime())
        if test_ID in [0, 2]:
            for depth in range(1, m_depth+1):
                rows = [[0,0,0]]
                for num_tx in tx_range:
                    os.system("sudo mn -c")
                    result = tx_run(depth, num_tx)
                    rows.append([num_tx, result[0], result[1]])
                    time.sleep(100)
                with open("/home/mininet/Analysis/tree_{}_depth_ETH_statistics_{}.csv".format(depth, unique), 'w') as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(fields)
                    csvwriter.writerows(rows)
                make_plots("/home/mininet/Analysis/tree_{}_depth_ETH_statistics_{}.csv".format(depth, unique), yaxis='custom')
                data[2**depth] = rows
            make_parametric_plots("/home/mininet/Analysis/tree_parametric_ETH_statistics_{}_{}".format(depth, unique), "Peer(s)", data, fields, 'lower right')
        if test_ID in [0, 3]:
            for depth in range(1, m_depth+1):
                faultlink_rows = [[0,0,0]]
                for num_tx in tx_range:
                    os.system("sudo mn -c")
                    result = faultlink_tx_run(depth, num_tx)
                    faultlink_rows.append([num_tx, result[0], result[1]])
                    time.sleep(100)
                with open("/home/mininet/Analysis/faultlink_tree_{}_depth_ETH_statistics_{}.csv".format(depth, unique), 'w') as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(fields)
                    csvwriter.writerows(faultlink_rows)
                make_plots("/home/mininet/Analysis/faultlink_tree_{}_depth_ETH_statistics_{}.csv".format(depth, unique), yaxis='custom')            
                faultlink_data[2**depth] = faultlink_rows
            make_parametric_plots("/home/mininet/Analysis/faultlink_tree_parametric_ETH_statistics_{}_{}".format(depth, unique), "Peer(s)", faultlink_data, fields, 'lower right')
        os.system("sudo mn -c")


