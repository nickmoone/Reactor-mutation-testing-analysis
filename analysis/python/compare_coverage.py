import csv
import os
import sys
from html.parser import HTMLParser

glob_reactive_killed = 0
glob_reactive_mutations = 0

glob_noreactive_killed = 0
glob_noreactive_mutations = 0

""" Split string by delimiter and keep delimiter.
"""
def split_keep(string, delimiter):
    return [delimiter + s for s in string.split(delimiter) if s]

""" HTML parser that finds the mutation coverage shown in a index.html file.
"""
class PITReactorCompareReactiveParser(HTMLParser):
    def __init__(self):
        super(PITReactorCompareReactiveParser, self).__init__(convert_charrefs=True)
        self.result = {}
        self.killed = 0
        self.mutations = 0
        self.use_data = False
        self.n_data_found = 0

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            for attr, value in attrs:
                if attr == "class" and value == "coverage_legend":
                    self.use_data = True
        else:
            self.use_data = False

    def handle_endtag(self, tag):
        if tag == "div":
            self.use_data = False

    def handle_data(self, data):
        if self.use_data:
            if self.n_data_found == 1: # Only use the second finding because this is the mutation coverage.
                self.killed += int(data.split("/")[0])
                self.mutations += int(data.split("/")[1])
            self.n_data_found += 1


""" Get paths to reactive and no-reactive index.html reports and return in list of tuples.
    Only gets the most outer index.html (the one that is Package Summary).
"""
def get_filepaths(reactive_root, noreactive_root):
    filepaths = []

    # Find all reactive index.html project summary reports and search for no-reactive equivalent.
    for subdir, _, files in os.walk(reactive_root):
        for file in files:
            if file.endswith("index.html") and "Project Summary" in open(os.path.join(subdir,file), "r").read():
                reactive = os.path.join(subdir, file)
                noreactive = os.path.join(noreactive_root + subdir.split(reactive_root)[1], file)

                # Check if the no-reactive index.html exists for this reactive index.html.
                if not os.path.exists(noreactive):
                    exit("No-reactive index.html:\n" + noreactive + " does not exist for the reactive index.html:\n" + reactive)

                filepaths.append((reactive, noreactive))

    return filepaths


if __name__ == "__main__":
    if len(sys.argv) > 3:
        reactive_root = sys.argv[1]
        noreactive_root = sys.argv[2]
        csvpath = sys.argv[3]

        filepaths = get_filepaths(reactive_root, noreactive_root)

        with open(csvpath, "w") as csvfile:
            header = ["no-reactive report", "reactive report", 
                    "mutations (no-reactive)", "mutations (reactive)", "diff mutations (reactive - no-reactive)",
                    "killed (no-reactive)", "killed (reactive)", "diff killed (reactive - no-reactive)",
                    "% killed (no-reactive)", "% killed (reactive)", "diff % killed (reactive - no-reactive)"]
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for reactive_path, noreactive_path in filepaths:
                parser = None
                with open(reactive_path, "r", encoding='utf-8') as reactive_file:
                    with open(noreactive_path, "r", encoding='utf-8') as noreactive_file:
                        # Sum coverage numbers.
                        reactive_parser = PITReactorCompareReactiveParser()
                        reactive_parser.feed(reactive_file.read().replace('\n', ''))
                        glob_reactive_killed += reactive_parser.killed
                        glob_reactive_mutations += reactive_parser.mutations

                        noreactive_parser = PITReactorCompareReactiveParser()
                        noreactive_parser.feed(noreactive_file.read().replace('\n', ''))
                        glob_noreactive_killed += noreactive_parser.killed
                        glob_noreactive_mutations += noreactive_parser.mutations

                        row = [split_keep(noreactive_path, "/no-reactive/")[-1], split_keep(reactive_path, "/reactive/")[-1],
                            noreactive_parser.mutations, reactive_parser.mutations, reactive_parser.mutations - noreactive_parser.mutations,
                            noreactive_parser.killed, reactive_parser.killed, reactive_parser.killed - noreactive_parser.killed,
                            round(noreactive_parser.killed/noreactive_parser.mutations*100, 2), round(reactive_parser.killed/reactive_parser.mutations*100, 2), round((reactive_parser.killed/reactive_parser.mutations*100) - (noreactive_parser.killed/noreactive_parser.mutations*100), 2)]

                        writer.writerow(row)

            # Calculate percentage and export results.
            writer.writerow([])
            row = ["TOTAL", "TOTAL", glob_noreactive_mutations, glob_reactive_mutations, glob_reactive_mutations - glob_noreactive_mutations,
                glob_noreactive_killed, glob_reactive_killed, glob_reactive_killed - glob_noreactive_killed,
                round(glob_noreactive_killed/glob_noreactive_mutations*100, 2), round(glob_reactive_killed/glob_reactive_mutations*100, 2), round((glob_reactive_killed/glob_reactive_mutations*100) - (glob_noreactive_killed/glob_noreactive_mutations*100), 2)]

            writer.writerow(row)
    else:
        exit("Usage: python compareCoverage.py <reactive_root> <noreactive_root> <csvpath>")

    

