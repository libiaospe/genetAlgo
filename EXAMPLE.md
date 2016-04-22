# Example

## Below is a minimal example demonstrating how to specify required input arguments. 

- *genetAlgo* has two required two input file, a configuration file in plain text (*.config) and a python file (*.py) implementing the fitness function

- The config file is used to define the paramter space. For any parameter 'x' which can take its value within a range, use the format _x=[lower-bound, upper-bound]|num_, where 'x' denotes the actual name of parameter which has to be exactly matched with that used in the fitness function, 'lower' and 'upper' bounds constrain the range, and 'num' is the total number of evenly-spaced values within the range. For explicitly specifying each value, use _x=[v1, v2, v3, v4,...]_. For any paramter that takes a fixed value, use _x=value_. **Note that** each paramter **must** take a total number of 2^n (e.g. 1,2,4,8,16,...) possible values. For an example see [here](https://github.com/libiaospe/genetAlgo/blob/master/codes/example.config).

- A Python file is required to implement how to calculate the fitness of each different combination of parameter values. **Note that** fitness should be evaluated on positive real numbers and coded as the smaller the better. For more details and an example see [here](https://github.com/libiaospe/genetAlgo/blob/master/codes/fitnessFunc.py)

- An optional population file (*.pop) can also be provided to use as the initial setting of the ancestral population. After finishing to run, the ending population at the last generation is automatically saved into a population file. If the optimization result is not satisfactory, one can carry on further running the algorithm again by loading the ending population of last run as the initial population of the new run. 

- For details about all the other command options, go to the source code folder, run `python GeneticAlgorithm.py -h` and refer to the screen message. 