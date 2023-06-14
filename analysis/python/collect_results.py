import os
import shutil
import sys
from pathlib import Path


""" Find and sort a list of timestamps in a reports directory.
"""
def get_timestamps(dir):
    timestamps = os.listdir(dir)
    timestamps.sort(reverse=True)
    return timestamps

""" Return true if file string is a results html file (so no index).
"""
def is_results_html(file):
    return file.endswith(".html") and not file.endswith("index.html")

""" Return true if there is an index.html for this timestamp, otherwise it contains no results.
"""
def is_valid_timestamp_dir(dir):
    return os.path.isdir(dir) and "index.html" in os.listdir(dir)

""" Return true if the reactor reactive mutator was active for this result file.
"""
def mutator_active_in_file(file):
    return "<li class='mutator'>REACTOR_REACTIVE_MUTATOR</li>" in file.read()


def iterate_files(project_root, dest):
    # First find a target/pit-reports folder in the project.
    for dir, _, _ in os.walk(project_root):
            if dir.endswith("target/pit-reports"):
                report_mutator_active = None
                report_mutator_inactive = None
                timestamps = get_timestamps(dir)

                # Iterate timestamps to find the latest mutator active and mutator inactive report.
                for timestamp in timestamps:
                    # Iterate all timestamps until we have a report with the mutator active and a report with the mutator inactive.
                    if not report_mutator_active or not report_mutator_inactive:
                        if is_valid_timestamp_dir(dir + "/" + timestamp):
                            # Find the first html file that is not index.html to check if the mutator was active.
                            for dir2, _, files in os.walk(dir + "/" + timestamp):
                                for file in files:
                                    if is_results_html(file):
                                        f = open(dir2 + "/" + file, "r")
                                        if mutator_active_in_file(f):
                                            if not report_mutator_active:
                                                report_mutator_active = timestamp
                                        else:
                                            if not report_mutator_inactive:
                                                report_mutator_inactive = timestamp
                                        break
                    else:
                        break

                if len(timestamps) > 0:
                    # Check if there are reports for active and inactive after iterating reports.
                    if report_mutator_active is None or report_mutator_inactive is None:
                        exit("Missing a report for REACTIVE_MUTATOR active or a report for REACTIVE_MUTATOR inactive.\nin " + dir)

                    # Copy reports to reactive and non-reactive subfolders of destination.
                    # print("Active report for", dir, "is", report_mutator_active)
                    # print("Inactive report for", dir, "is", report_mutator_inactive)
                    shutil.copytree(dir + "/" + report_mutator_active, dest + "/reactive/" + project_root.split("/")[-1] + dir.split(project_root)[1])
                    shutil.copytree(dir + "/" + report_mutator_inactive, dest + "/no-reactive/" + project_root.split("/")[-1] + dir.split(project_root)[1])


if __name__ == "__main__":
    if len(sys.argv) > 2:
        project_root = sys.argv[1]
        result_dest = sys.argv[2]
        filepaths = iterate_files(project_root, result_dest)
    else:
        exit("Usage: python collectHTML.py <project_root> <result_dest>")

