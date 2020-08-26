import sys
import os
import csv
import time
from tree_N_depth_M_transactions_NXT import run as tx_run
from tree_NXT_with_link_up_and_down import run as faultlink_tx_run
from n_star_topology_NXT import run as star_run
from Analysis.make_plots import make_plots
from Analysis.make_plots import make_parametric_plots


if __name__=="__main__":
    if len(sys.argv) != 2:
        # print("Usage: sudo python ./{} <maximum_star> <maximum_tree_depth> <maximum_num_tx>".format(sys.argv[0]))
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
                # os.system("""sudo lsof | grep "(deleted)$" | sed -re 's/^\S+\s+(\S+)\s+\S+\s+([0-9]+).*/\1\/fd\/\2/' | while read file; do sudo bash -c ": > /proc/$file"; done""")
                os.system("sudo mn -c")
                # os.system("sudo /home/mininet/kill_monitors.sh &> /dev/null")
                # os.system("sudo rm -f /home/mininet/Proc_Logs/* &>/dev/null")
                # functionInProcess(star_run, [i])
                star_run(i)
                time.sleep(100)
                # os.system("sudo python n_star_topology_NXT.py {}".format(i))
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
                    # os.system("""sudo lsof | grep "(deleted)$" | sed -re 's/^\S+\s+(\S+)\s+\S+\s+([0-9]+).*/\1\/fd\/\2/' | while read file; do sudo bash -c ": > /proc/$file"; done""")
                    os.system("sudo mn -c")
                    # os.system("sudo /home/mininet/kill_monitors.sh &> /dev/null")
                    # os.system("sudo rm -f /home/mininet/Proc_Logs/* &>/dev/null")
                    # result = functionInProcess(tx_run, [depth, num_tx])
                    result = tx_run(depth, num_tx)
                    rows.append([num_tx, result[0], result[1]])
                    time.sleep(100)
                with open("Analysis/tree_{}_depth_NXT_statistics_{}.csv".format(depth, unique), 'w') as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(fields)
                    csvwriter.writerows(rows)
                make_plots("Analysis/tree_{}_depth_NXT_statistics_{}.csv".format(depth, unique), yaxis='ETH')
                data[2**depth] = rows
            make_parametric_plots("Analysis/tree_parametric_NXT_statistics_{}_{}".format(m_depth, unique), "Peer(s)", data, fields, 'lower right')
        if test_ID in [0, 3]:
            for depth in range(1, m_depth+1):
                faultlink_rows = [[0,0,0]]
                for num_tx in tx_range:
                    os.system("sudo mn -c")
                    result = faultlink_tx_run(depth, num_tx)
                    faultlink_rows.append([num_tx, result[0], result[1]])
                    time.sleep(100)
                with open("Analysis/faultlink_tree_{}_depth_NXT_statistics_{}.csv".format(depth, unique), 'w') as f:
                    csvwriter = csv.writer(f)
                    csvwriter.writerow(fields)
                    csvwriter.writerows(faultlink_rows)
                make_plots("Analysis/faultlink_tree_{}_depth_NXT_statistics_{}.csv".format(depth, unique), yaxis='ETH')
                faultlink_data[2**depth] = faultlink_rows
            make_parametric_plots("Analysis/faultlink_tree_parametric_NXT_statistics_{}_{}".format(m_depth, unique), "Peer(s)", faultlink_data, fields, 'lower right')
        os.system("sudo mn -c")
        # os.system("sudo /home/mininet/kill_monitors.sh &> /dev/null")
        # os.system("sudo rm -f /home/mininet/Proc_Logs/* &>/dev/null")
