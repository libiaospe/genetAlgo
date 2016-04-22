'''
Note:
1.  Do not modify the function name or its argument list.
2.  Save the calculated fitness score to parameter 'fitness' (as shown below)
3.  Use parDict['x'] to access value of parameter 'x'
4.  Do not modify last line 'return fitness'
'''


def fitnessFunc(parDict):
    
##################### Do NOT change anything ABOVE #####################    
    
    
    
    fitness = (parDict['a'] * (parDict['b']**0.5) * parDict['c'] * parDict['d'] + parDict['e'] - len(parDict['f']))**0.5
        
    
        

##################### Do NOT change anything BELOW #####################       
        
    return fitness