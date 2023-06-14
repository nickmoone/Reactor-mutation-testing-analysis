import csv
import os
import sys

glob_result = [0, 0, 0, 0, 0, 0, 0, 0, 0]

""" Get all paths to compare_coverage.csv files in root (sub)folders.
"""
def get_files(root):
    filepaths = []

    for subdir, _, files in os.walk(root):
        for file in files:
            if file.endswith("compare_coverage.csv"):
                filepaths.append((subdir.split("/")[-1], os.path.join(subdir, file)))

    return filepaths


""" Read the compare_coverage.csv file and add values to the global result.
"""
def handle_csv(project, file, writer):
    lines = file.readlines()
    if len(lines) != 0:
        last_line = lines[-1]
        reader = csv.reader([last_line])

        data = next(reader)

        for i in range(2, len(data)):
            glob_result[i - 2] += float(data[i])
        writer.writerow([project, ""] + data[2:])


if __name__ == "__main__":
    if len(sys.argv) > 2:
        root = sys.argv[1]
        csv_path = sys.argv[2]

        with open(csv_path, "w") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(["project", "", "mutations (no-reactive)", "mutations (reactive)", "diff mutations (reactive - no-reactive)", "killed (no-reactive)", "killed (reactive)", "diff killed (reactive - no-reactive)", "% killed (no-reactive)", "% killed (reactive)", "diff % killed (reactive - no-reactive)"])
            for project, filepath in get_files(root):
                with open(filepath, "r", encoding='utf-8') as file:
                    handle_csv(project, file, writer)

            for i in range(0, 6):
                glob_result[i] = int(glob_result[i])
            glob_result[6] = round(glob_result[3] / glob_result[0] * 100, 2)
            glob_result[7] = round(glob_result[4] / glob_result[1] * 100, 2)
            glob_result[8] = round((glob_result[4] / glob_result[1] * 100) - (glob_result[3] / glob_result[0] * 100), 2)


            writer.writerow([])
            writer.writerow(["TOTAL", ""] + glob_result)

    else:
        exit("Usage: python countMethods.py <results_path> <csv_path>")
