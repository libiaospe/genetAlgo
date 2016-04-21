#!/usr/bin/env python

'''
Author: Biao Li (2016)

Purpose: Implementation of genetic algorithm for searching optimized parameter combinations

Description:
'''

import random, os, sys, pickle, math, copy
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
import sqlite3

try:
    import progressbar
    useProgressBar = True
except:
    useProgressBar = False
    logging.warning("Fail to import 'progressbar' module, progress bar will not be shown")

options = []


class Simulator():
    def __init__(self, paramDict, numTopFitToSave=10, saveAt=1, initPopFile=None, outFile='result'):
        '''
        Args: see self.evalFitness(...)
            initPopFile -- file name of initial population. Load it as the
                parameter setting of the ancestral gen if given (default:None)
        '''
        self.paramDict = paramDict
        self.numTopFitToSave = numTopFitToSave
        self.saveAt = saveAt
        self.outFile = outFile
        
        self.topFitness, self.topPars = [], [] # lists of top fitness values and their associated param combos
        self.initPopFile = initPopFile
        
        return
    
    
    def initPop(self, paramDict, popSize):
        '''
        convert and translate the input parameter space to the initial population
        Note: each value in paramDict must be a list that has 2^n elements, where n = 1,2,3,...
        '''
        # load an external file with a saved pop (optional)
        if self.initPopFile:
            with open(self.initPopFile, 'rb') as fi:
                tmpPop = pickle.load(fi)
            
            if popSize > len(tmpPop): # add duplicates randomly to meet the popSize requirement
                N = popSize - len(tmpPop)
                if N <= len(tmpPop):
                    addInds = random.sample(tmpPop, N)
                    tmpPop.extend(addInds)
                else:
                    idxes = [random.randint(0, len(tmpPop)-1) for i in range(N)]
                    [tmpPop.append(tmpPop[i]) for i in idxes]
            
            else:  # randomly remove inds from 'tmpPop' to meet the popSize requirement
                random.shuffle(tmpPop)
                tmpPop = tmpPop[:popSize]
            
            return tmpPop

        # generate individuals in terms of chromosomes in binary format
        pars = paramDict.keys()
        pop = [{} for idx in range(popSize)]
        
        for par in pars:
            # check if paramDict[par] has 2^n elements
            n = math.log(len(paramDict[par]), 2)
            
            if math.ceil(n) != math.floor(n):
                raise ValueError("parameter %s need to be specified 2^n possible values or set to be fixed" % par)
            
            # total number of possible values for par in decimal form
            maxDec = len(paramDict[par]) - 1
            
            # length of chr for par in binary form
            lenChr = len(bin(maxDec).split('b')[-1])
            
            # assign par/geno (binary) to each individual randomly 
            for idx in range(len(pop)):
                rand = random.randint(0, maxDec)
                tmp = bin(rand).split('b')[-1]
                pop[idx][par] = (lenChr - len(tmp)) * '0' + tmp

        return pop        

    
    def _convertBinToPar(self, individual):
        '''
        convert binary coding of individual obj to input param dict required by
        ascerBias simulation.
        '''
        parDict = {}
        
        for key, value in zip(individual.keys(), individual.values()):
            binNum = '0b'+value
            decNum = int(binNum, 2)
            parDict[key] = self.paramDict[key][decNum]
        
        return parDict
             
    
    def evalFitness(self, individual, fixParamDict, fitnessFunc):
        '''
        pass in a function to evaluate the fitness of the individual (represented by a parameter combination)
        '''
        # convert binary values to indexes for varied pars
        parDict = self._convertBinToPar(individual)
        
        # set fixed pars
        for par, value in zip(fixParamDict.keys(), fixParamDict.values()):
            parDict[par] = value
            
        # calculate the fitness value
        try:
            fitness = fitnessFunc(parDict)
        except:
            raise ValueError("Check Input! Fitness function fails to run on the following parameter combination!\n%s" % '\n'.join(["{} = {}".format(i,j) for i,j in zip(parDict.keys(), parDict.values())]))
        
        # save top 'numTopFitToSave' fitness values and parCombos to self.topFitness and self.topPars
        if len(self.topFitness) < self.numTopFitToSave and parDict not in self.topPars:
            self.topFitness.append(fitness)
            self.topPars.append(parDict)
        
        else:
            maxFit = max(self.topFitness)
            idxMaxFit = self.topFitness.index(maxFit)
            if fitness < maxFit and parDict not in self.topPars:
                del self.topFitness[idxMaxFit]
                del self.topPars[idxMaxFit]
                self.topFitness.append(fitness)
                self.topPars.append(parDict)
        
        return fitness
    
    
    def diffParamType(self, paramSpaceDict):
        '''
        Differentiate two different types of parameters, variable ones and fixed ones.
        Return two dict objs with the first as dict containing variable parameters and
        the second as dict having fixed parameters 
        '''
        varParamDict = {}
        fixParamDict = {}
        
        for par, value in zip(paramSpaceDict.keys(), paramSpaceDict.values()):
            try:
                assert len(value) > 1
                varParamDict[par] = value
            except:
                fixParamDict[par] = value[0] if type(value) in (list, tuple) else value
            #        
            if varParamDict.has_key(par) and len(varParamDict[par]) % 2 != 0:
                raise ValueError("Parameter %s specified in the parameter space need to be either a single element or a list of 2^n elements" % par)
        
        return varParamDict, fixParamDict
        
    
    def evolve(self, numGen, popSize, probCross, probMut, fitnessFunc):
        '''
        Arguments:
            numGen -- number of generations to evolve
            popSize -- population size
            probCross -- probability of crossover occurring at each mating event
            probMut -- probability of point mutation occurring at each binary site
            fitnessFunc -- func obj to evaluate individual's fitness 
        '''
        # separate variable parameters from fixed parameters
        tmp = self.diffParamType(self.paramDict)
        varParamDict = tmp[0]
        fixParamDict = tmp[1]
        
        # create initial population from 'varParamDict'
        pop = self.initPop(varParamDict, popSize)
        
        # evaluate fitness for ancestral pop/initial pop
        if useProgressBar:
            progMes = "Evolving the ancestral population"
            pbar = progressbar.ProgressBar(widgets=[progMes, ' ', progressbar.Percentage(), ' ', progressbar.Bar('.'), ' ', progressbar.ETA(), ' '], maxval=len(pop)).start()
            
        fitness = []
        for idx, ind in enumerate(pop):
            fitness.append(self.evalFitness(ind, fixParamDict=fixParamDict, fitnessFunc=fitnessFunc))
            #
            if useProgressBar:
                pbar.update(idx+1)
        if useProgressBar:
            pbar.finish()
        
        # evolve 'numGen' generations
        if useProgressBar:
            progMesGen = "Evolving the population for %d generations" % numGen
            pbar = progressbar.ProgressBar(widgets=[progMesGen, ' ', progressbar.Percentage(), ' ', progressbar.Bar('.'), ' ', progressbar.ETA(), ' '], maxval=numGen).start()
        #
        for idx, gen in enumerate(range(1, numGen+1)):
            children = []
            # fill up the offspring generation
            while len(children) < popSize:
                parents = self.chooseMatingInds(pop=pop, fitness=fitness, numInd=2)
                offspring = self.crossover(parents, probCross)
                self.mutation(offspring, probMut) # number of individuals-2
                # add generated offspring to next gen
                children.extend(offspring)
            # {end while}
            # evaluate fitness for generation 'gen'
            fitness = []
            for ind in children:
                fitness.append(self.evalFitness(ind, fixParamDict=fixParamDict, fitnessFunc=fitnessFunc))
           
            # start the next generation
            pop = children
            # update progress bar
            if useProgressBar:
                pbar.update(idx+1)
            
            # save topfit and current pop
            if gen % self.saveAt == 0:
                self._saveTopFits()
                self._saveCurrPop(pop)
            
        if useProgressBar:
            pbar.finish()
        return pop, fitness      
      
    
    def _saveCurrPop(self, pop):
        '''
        save current population via pickle
        '''
        with open(self.outFile+'.pop', 'wb') as fi:
            pickle.dump(pop, fi)
        return
    
    
    def _saveTopFits(self):
        '''
        save parameter combinations of top fits
        '''
        topFitness, topPars = copy.deepcopy(self.topFitness), copy.deepcopy(self.topPars)
        
        flag = len(topFitness)
        parFile = open(self.outFile+'.fit', 'w')
        pars = self.topPars[0].keys()
        parFile.write('\t'.join(['fitness'] + pars) + '\n')
        
        while flag > 0:
            idx = topFitness.index(min(topFitness))
            parFile.write("%.6f\t" % topFitness[idx])
            parFile.write('\t'.join([str(topPars[idx][p]) for p in pars]) + '\n')
            del topFitness[idx]
            del topPars[idx]
            
            flag -= 1
            
        parFile.close()
        
        return    
    
    
    def crossover(self, parents, probCross):
        '''
        perform mating and 'crossover' between parents and return two offspring.
        The crossover here is single-point crossover. 
        '''
        offspring1 = {}
        offspring2 = {}
        parent1 = parents[0]
        parent2 = parents[1]
        #
        pars = parent1.keys()
        for par in pars:
            chr1 = parent1[par]
            chr2 = parent2[par]
            # if the length of binary seq == 1 (two values specified for par), parent1 passes par to offspring 2 and parent2 to offspring 1 if random() < probCross
            if len(chr1) == 1:
                if random.random() < probCross:    
                    offChr1 = chr2
                    offChr2 = chr1
                else:
                    offChr1 = chr1
                    offChr2 = chr2
            elif random.random() < probCross:
                position = random.randint(1, len(chr1)-1)
                offChr1 = chr1[:position] + chr2[position:]
                offChr2 = chr2[:position] + chr1[position:]
            else:
                offChr1 = chr1
                offChr2 = chr2
            #
            offspring1[par] = offChr1
            offspring2[par] = offChr2
        #
        return [offspring1, offspring2]
        
    
    def mutation(self, individuals, probMut):
        '''
        perform point mutations among individuals 
        '''
        pars = individuals[0].keys()
        for ind in individuals:
            for par in pars:
                chr = ind[par]
                for idx in xrange(len(chr)):
                    if random.random() < probMut:
                        if chr[idx] == '0':
                            chr = chr[:idx] + '1' + chr[idx+1:]
                        else:
                            chr = chr[:idx] + '0' + chr[idx+1:]
                    #
                ind[par] = chr
            # {end For: par}
        # {end For: ind}
        return                
                        
        
    def chooseMatingInds(self, pop, fitness, numInd):
        '''
        stochastic sampling for 'numInd' individuals according to fitness values with replacement (roulette wheel selection)
        '''
        recipFitness = [1./fit for fit in fitness]
        sumRecFit = sum(recipFitness)
        weight = [i/sumRecFit for i in recipFitness]
        roulette = [sum(weight[:i]) for i in xrange(1, len(weight)+1)]
        #
        matingInds = []
        for num in xrange(numInd):
            rand = random.random()
            try:
                idx = [rand < i for i in roulette].index(True)
                matingInds.append(pop[idx])
            except:
                matingInds.append(pop[-1])
        #
        return matingInds
        

def createParamCombo(parRange, num):
    '''
    create 'num' evenly distributed values within parameter range
    '''
    try:
        interval = (parRange[1] - parRange[0]) / float(num-1)
        return [parRange[0] + i*interval for i in xrange(num)]
    except:
        if num == 1 and parRange[0] == parRange[1]:
            return [parRange[0]]
        else:
            raise ValueError("need to check input parRange or num")
        

def _cleanFormat(item):
    '''
    return everything in string format.
    if item is int: remove decimal part
    if item is float: keep 6 decimals
    if item is list/tuple: remove '()'/'[]'
    '''
    try:
        tmp = int(item)
        return str(tmp)
    except:
        pass
    #
    try:
        tmp = float(item)
        return '%.6f' % round(tmp, 6)
    except:
        pass
    #
    if (item.startswith('[') and item.endswith(']')) or (item.startswith('(') and item.endswith(')')):
        tmp = item[1:-1].split(',')
        tmp = [_cleanFormat(i) for i in tmp]
        return ','.join(tmp)
    else:
        raise ValueError("item need to be an integer, a float number or a string of number or a string of list/tuple object")
    #   
    

def saveParsToDB(fileName, tableName='pars'):
    '''
    save parameters in csv format to database
    '''
    with open(fileName, 'r') as fi:
        lines = fi.readlines()
        #lines = lines[1:]
        for idx, line in enumerate(lines):
            lines[idx] = line.split('\t')
            if lines[idx][-1] == '\n':
                lines[idx].remove('\n')
            else:
                lines[idx][-1] = lines[idx][-1].split('\n')[0]
        if lines[-1] == []:
            lines.remove([])
        fi.close()

    title = lines[0]
    values = lines[1:]
    #
    values = [[_cleanFormat(i) for i in j] for j in values]
    #
    connection = sqlite3.connect(fileName+'.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS {}".format(tableName))
    #  
    tmp = "CREATE TABLE {}".format(tableName) + '(' + ','.join(['Id INT'] + [i+' '+'TEXT' for i in title]) + ')'
    cursor.execute(tmp)
    pars = [[idx+1] + ind for idx, ind in enumerate(values)]
   
    tmp = "INSERT INTO {} VALUES".format(tableName) + '(' + ','.join(['?'] * len(pars[0])) + ')'
    cursor.executemany(tmp, pars)
    
    # commit changes and close connection
    connection.commit()
    connection.close()
    return 


if __name__ == '__main__':
    
    
    ####################### 04-15-2016 ###################
    ## Step 1 - parse argument (including parameter file, fitness_function.py, command opt - numGene, popSize, probCross, probMut, output, savePop, loadPop, numTopFitToSave)
    
    ## step 2 - get fitness function
    
    def getFitnessFunc(target = 0):
        
        def fitnessFunc(parDict):
            fitness = (parDict['a'] * (parDict['b']**0.5) * parDict['c'] * parDict['d'] + parDict['e'])**0.5
            return fitness
    
        return fitnessFunc
    
    fitnessFunc = getFitnessFunc()
    
    ## step 3 - config Simulator
    numGen = 50
    popSize = 50
    
    # paramDict: a - range(1, 16), b - range(11,18), c - constant = 2.5
    paramDict = {}
    paramDict['a'] = [int(i) for i in createParamCombo([1, 64], 64)]
    paramDict['b'] = [int(i) for i in createParamCombo([11, 18], 8)]
    paramDict['c'] = [2.5]
    paramDict['d'] = [int(i) for i in createParamCombo([100, 200], 128)]
    paramDict['e'] = 1.25
    
    simu = Simulator(paramDict, numTopFitToSave=25, saveAt=5, initPopFile='result.pop')
    
    ## step 4 - evolve
    tmp = simu.evolve(numGen=numGen, popSize=popSize, probCross=.5, probMut=.05, fitnessFunc=fitnessFunc)
    
    ## step 5 - save results to db
    saveParsToDB('result.fit', 'result')
    
    sys.exit()
    
    
    
    
    