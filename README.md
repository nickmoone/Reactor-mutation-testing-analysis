# Run and analyse Pitest for Project Reactor research
This repository contains scripts for analysing the effectiveness of mutation testing for reactive programming.

The scripts in <em>/setup</em> clone a list of projects from GitHub, add our created [Pitest plugin for mutating Project Reactor reactive method calls (Pitest-Reactor)](https://github.com/nickmoone/Pitest-Reactor) to the <em>pom.xml</em> of all projects, and run Pitest on all projects. 

The scripts in <em>/analysis</em> extract all Pitest results from the projects, exports general mutation statistics to CSV, and exports mutation statistics specific for Project Reactor reactive method calls to CSV.

## Setup

### Downloading projects
Running <em>download_projects.sh</em> requires a file containing a list of GitHub clone URLs to projects that will be cloned into a specific folder.

### Adding Pitest-Reactor to projects
To add Pitest-Reactor to the projects <em>add_pitest_to_projects.sh</em> can be used, this script adds the plugin snippet in <em>/setup/plugin-snippet.xml</em> to the plugins section of the <em>pom.xml</em> of each project.

### Changing Pitest mutators
To change the mutator used by Pitest-Reactor in all projects <em>change_mutator_projects.sh</em> can be used, this script changes the <em>mutator</em> tag of the Pitest-Reactor plugin of each project.

### Running projects
To run Pitest on all projects <em>run_projects.sh</em> is used, this script executes command <em>mvn test-compile org.pitest:pitest-maven:mutationCoverage</em> inside all project folders.

## Analysis

### Collecting Pitest results
Running <em>collect_results.py</em> with the root folder of a project as input will generate a destination folder that has two sub-folders (<em>reactive</em> and <em>no-reactive</em>). Inside these folders a new project folder is created for this project, this folder has the full structure of the original project but only contains the Pitest reports of the project.
When an error with message "Missing a report for REACTIVE_MUTATOR active or a report for REACTIVE_MUTATOR inactive." is produced, a report with or without REACTOR_REACTIVE_MUTATOR was missing in the project. This means Pitest wasn't (correctly) used with or without the mutator in this project.

### Counting reactive methods mutation coverage
After collecting the Pitest HTML result files, running <em>count_methods.py</em> with the results folder (the folder that contains a reactive and a no-reactive folder) as input will count for each reactive method call (in Flux or Mono class) how many times they are killed, survived, or timed_out. The results are written to a CSV file.

### Comparing Pitest vs Pitest-Reactor mutation coverage
After collecting the Pitest HTML result files, runing <em>compareReactive.py</em> with the results folder (the folder that contains a reactive and a no-reactive folder) as input compares the mutation coverage results of reactive projects when using default mutators and when using default mutators + Pitest-Reactor mutators.


## Tests of scripts
### collect_results.py
This code is tested by running it on a project with a known file structure and where the folder containing the newest reactive and no-reactive results are known. After running the algorithm on the project the results folder contained the Pitest reports of the correct timestamps with the expected folder structure.

### count_methods.py
This code is tested by running it on a project results folder (created by <em>collect_results.py</em>) and comparing its exported .csv to the statistics of the reactive results counted by hand. This matched exactly.

### compare_coverage.py
This code is tested by manually cheching all Project Summary index.html files in the results folder (created by <em>collect_results.py</em>) of a test project and comparing it to the exported .csv. The sum values is checked by comparing it to the manually added mutation coverage values of all projects.
