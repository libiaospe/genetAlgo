# genetAlgo

A Python program implementing the genetic algorithm as a search heuristic that mimics the process of natural selection for optimization and parameter search problems. 

- For source code, please go to: (https://github.com/libiaospe/genetAlgo/tree/master/codes)
- For reporting any issue: use (https://github.com/libiaospe/genetAlgo/issues)
- See below for installing dependencies and a quick start guide

## Install Dependencies
- Install Python ([Anaconda Python](https://www.continuum.io/downloads) is highly recommended. If you don't have time or disk space for the entire distribution, install [Miniconda](http://conda.pydata.org/miniconda.html) instead)
- Install *progressbar* module. Open a terminal and run
```
conda install progressbar
```

## Quick start guide
1. Download [genetAlgo program folder] (https://github.com/libiaospe/genetAlgo/archive/master.zip)
2. Unzip and go to /genetAlgo/codes/
3. Create parameter space configuration file and fitness function fiel, see [an example](https://github.com/libiaospe/genetAlgo/blob/master/EXAMPLE.md)
4. Run `python GeneticAlgorithm.py -h` for how to specify command options.

5. Test run the example below and view the result file of optimized paramters that attain best fits
```
python GeneticAlgorithm.py -c example.config -f fitnessFunc.py -s 100 -g 100 -r 0.5 -m 0.05 -n 200 -o result -a 5
vim result.fit
```
6. If there is any bug, please rerun by appending _--debug_ to the end of the command, copy and paste the screen out, and report the issue.  




