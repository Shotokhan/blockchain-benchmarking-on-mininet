import csv
import os
import sys


# I use "sudo -su mininet" before tshark to not have security warnings
def tshark_output_to_CSV(out_fullpath, capture_fullpath, filt=None):
    out_filename = out_fullpath.split("/")[-1]
    user = "mininet"
    if filt is None:
        os.system("echo $(sudo -su {} tshark -q -r '{}' -z conv,ip) > /tmp/{}".format(user, capture_fullpath, out_filename))
    else:
        os.system("echo $(sudo -su {} tshark -q -r '{}' -z conv,ip,{}) > /tmp/{}".format(user, capture_fullpath, filt, out_filename))
    oneline = None
    with open("/tmp/{}".format(out_filename), 'r') as f:
        oneline = f.readlines()
    fields = ['Left peer', 'Right peer', 'Right to left frames', 'Right to left bytes', 'Left to right frames', 'Left to right bytes', 'Total frames', 'Total bytes', 'Relative start', 'Duration']
    oneline = oneline[0]
    ind = len(oneline) - oneline[-1::-1].find("|") - 1
    oneline = oneline[ind+1:]
    data = oneline.split(" ")
    data = list(filter(lambda f: f not in ['', '<->'], data))
    data = data[:-1]
    rows = [data[i*len(fields):(i+1)*len(fields)] for i in range(len(data) // len(fields))]
    with open("{}".format(out_fullpath), 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
    # os.system("sudo rm -f /tmp/{}".format(out_filename))


def tshark_total_traffic(capture_fullpath, filts):
    capture_name = capture_fullpath.split("/")[-1]
    user = "mininet"
    os.system("echo $(sudo -su {} tshark -q -r '{}' -z io,phs) > /tmp/{}".format(user, capture_fullpath, capture_name))
    oneline = None
    with open("/tmp/{}".format(capture_name), 'r') as f:
        oneline = f.readlines()
    oneline = oneline[0]
    total = 0
    for filt in filts:
        ind = oneline.find(filt)
        if ind != -1:
            bytes_ind = oneline.find("bytes", ind+1)
            finish_ind = oneline.find(" ", bytes_ind+1)
            bytes_string = oneline[(bytes_ind + 6):finish_ind]
            total += int(bytes_string)
    # os.system("sudo rm -f /tmp/{}".format(capture_name))
    return total


if __name__=="__main__":
    # tshark_output_to_CSV(*(sys.argv[1:]))
    print(tshark_total_traffic(sys.argv[1], sys.argv[2:]))
