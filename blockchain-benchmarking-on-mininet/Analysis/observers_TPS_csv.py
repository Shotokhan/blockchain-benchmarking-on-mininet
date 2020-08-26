import csv


def export_TPS_to_CSV(filename, observers):
    # observers is a dict with host as keys and TPS as values
    fields = ['Observer node', 'Measured TPS']
    rows = [[host, observers[host]] for host in observers.keys()]
    with open(filename, 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)
