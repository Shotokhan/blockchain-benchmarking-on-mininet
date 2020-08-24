import os
import sys
import csv


def time_to_num(time_str):
    hh, mm , ss = map(int, time_str.split(':'))
    return ss + 60*(mm + 60*hh)


def log_analysis(logfile, commands):
    logname = logfile.split("/")[-1]
    time_axis = []
    CPU_axis = []
    MEM_axis = []
    CPU_sum = 0
    MEM_sum = 0
    state = 'header'
    columns = ['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES', 'SHR', 'S', '%CPU', '%MEM', 'TIME+', 'COMMAND']
    CPU_ind = columns.index('%CPU')
    MEM_ind = columns.index('%MEM')
    command_ind = columns.index('COMMAND')
    base_timestamp = None
    first = 0
    with open(logfile, 'r') as f:
        line = f.readline()
        while line:
            line = line.split(" ")
            line = list(filter(lambda f: f != '', line))
            try:
                first = line[0]
            except IndexError:
                pass
            if first == 'top':
                if state == 'data':
                    CPU_axis.append(CPU_sum)
                    MEM_axis.append(MEM_sum)
                    if CPU_sum == 0 and MEM_sum == 0:
                        break
                state = 'header'
                CPU_sum = 0
                MEM_sum = 0
                timestamp = line[2]
                timestamp = time_to_num(timestamp)
                if base_timestamp is None:
                    base_timestamp = timestamp
                timestamp = timestamp - base_timestamp
                time_axis.append(timestamp)
            elif first == 'PID':
                state = 'data'
            elif state == 'data':
                try:
                    command = line[command_ind]
                    # there is the \n at the end of the string
                    command = command[:-1]
                    if command in commands:
                        CPU_perc = line[CPU_ind]
                        CPU_sum += float(CPU_perc)
                        MEM_perc = line[MEM_ind]
                        MEM_sum += float(MEM_perc)
                except IndexError:
                    pass
            line = f.readline()
    CPU_axis.append(CPU_sum)
    MEM_axis.append(MEM_sum)
    fields = ["Time(s)", "CPU%", "MEM%"]
    rows = [[str(time_axis[i]), str(CPU_axis[i]), str(MEM_axis[i])] for i in range(len(time_axis))]
    with open("/home/mininet/Analysis/analysis_{}.csv".format(logname), 'w') as f:
        # f.write("Time(s) CPU% MEM%" + os.linesep)
        csvwriter = csv.writer(f)
        '''
        for i in range(len(time_axis)):
            f.write("{} {} {}".format(str(time_axis[i]), str(CPU_axis[i]), str(MEM_axis[i])) + os.linesep)
        '''
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)


if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Usage: python proc_logs_analysis.py <logfile> <command1> ... <commandN>")
    else:
        logfile = sys.argv[1]
        commands = sys.argv[2:]
        log_analysis(logfile, commands)
        
