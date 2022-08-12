from cProfile import label
import enum
from operator import index
import os
import sys
import argparse
from turtle import color
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import re

'''
Author: Fernando Andrade
Date: Aug/09/2022
Collaborator/s:
Description: Read in hpc usage data from excel file and provide a visualization.
    The goal is to help visualize HPC allocated core hours vs actual core hours used.
    There is an additional metric for core hours used in just testing.

'''

# TODO discuss non-numerical icons in the core hour columns

comArgs = argparse.ArgumentParser(
    prog="usageVisual", description="Visualize hpc usage data.")
comArgs.add_argument('-f', '--filepath', type=str)
args = comArgs.parse_args()

# excel columns
hpcAccCol = 'HPCs/project-account'
allocCoreHrCol = 'Allocated core hours'
usedCoreHrCol = 'Used core hours'
testCoreHrCol = 'Core hours used for UFS-WM RT'
timePeriodCol = 'Time period'

# graph settings
barWidth = 0.3
barPadding = 3
xFontSize = 10
yFontSize = 16
xAxisFont = 20
yAxisFont = 20
titleFontSize = 24
legendFontSize = 14


def readData(filepath):
    '''Read in given excel file and return dataframe'''
    try:
        df = pd.read_excel(filepath, skiprows=[0])
    except Exception as e:
        print(e)
        sys.exit('Invalid filepath/filetype given. Exiting...')
        return
    df = df.fillna('N/A')
    return df


def sanitize(df):
    '''
        Remove rows that dont include hpc resource usage, using the HPC account column as the
        filter for now

        Parameters:
        df (object): pandas dataframe with the HPC usage data
    '''
    print('Cleaning up data...')
    print(df[hpcAccCol])

    # cut off rows that aren't for hpc usage (comments, empty lines, etc)
    try:
        removeIndex = df[hpcAccCol].tolist().index('N/A')
        print(
            f"First instance of N/A in HPC account column: {removeIndex}")
        print('Dropping invalid rows and showing result...')
        df = df.drop(df.index[removeIndex:])
    except:
        print('No empty HPC account values found, continuing to show result...')

    print(df)

    # clean up non numerical icons
    for hours in df[allocCoreHrCol].tolist():
        print(hours)
    print(df[allocCoreHrCol])

    print(df)
    print(df.columns.get_loc(usedCoreHrCol))
    return df


def getColVals(df, colName):
    '''

    '''
    colValues = []
    for value in df[colName].tolist():
        if(colName != timePeriodCol and colName != hpcAccCol):
            print(f'removing non numericals from {value}')
            print(value)
            if value != '' and value != 'N/A':
                colValues.append(int(re.sub('[^0-9]', '', str(value))))
            else:
                colValues.append(0)
        else:
            if 'Cheyenne' in value:
                colValues.append(value+'*')
            else:
                colValues.append(value)

    print(df[usedCoreHrCol], '\n')
    return colValues


def plotData(dataDict):
    '''

    '''
    print('plotting data...')
    print(dataDict)

    xlabels = (dataDict[timePeriodCol][i] + " " + dataDict[hpcAccCol][i]
               for i in range(len(dataDict[allocCoreHrCol])))

    barsAlloc = dataDict[allocCoreHrCol]
    barsUsed = dataDict[usedCoreHrCol]
    barsTest = dataDict[testCoreHrCol]

    allocSpacing = np.arange(len(dataDict[hpcAccCol]))
    usedSpacing = [val + barWidth for val in allocSpacing]
    testSpacing = [val + barWidth for val in usedSpacing]

    plt.bar(allocSpacing, barsAlloc, color='green',
            width=barWidth, label='Allocated Hours')
    plt.bar(usedSpacing, barsUsed, color='red',
            width=barWidth, label='Used Hours')
    plt.bar(testSpacing, barsTest, color='yellow',
            width=barWidth, label='Hours from testing')

    plt.xlabel('Timeframe & HPC / Account', fontsize=xAxisFont)
    plt.ylabel('Core Hours', fontsize=yAxisFont)
    plt.xticks(
        [r + barWidth for r in range(len(dataDict[allocCoreHrCol]))],  xlabels,  fontsize=xFontSize)
    plt.yticks(fontsize=yFontSize)
    plt.legend(fontsize=legendFontSize)
    plt.title('HPC Core Hour Usage', fontsize=titleFontSize)
    plt.show()


def main():
    df = readData(args.filepath)
    print(df)
    df = sanitize(df)

    timePeriods = getColVals(df, timePeriodCol)
    hpcAcc = getColVals(df, hpcAccCol)
    allocHrs = getColVals(df, allocCoreHrCol)
    usedHrs = getColVals(df, usedCoreHrCol)
    testHrs = getColVals(df, testCoreHrCol)

    print(f'Here are the time periods:\n{timePeriods}\n')
    print(f'Here are the HPCs and Accounts:\n{hpcAcc}\n')
    print(f'Here are the allocated hours:\n{allocHrs}\n')
    print(f'Here are the used hours:\n{usedHrs}\n')
    print(f'Here are the used hours for testing:\n{testHrs}\n')

    plotData({timePeriodCol: timePeriods, hpcAccCol: hpcAcc,
              allocCoreHrCol: allocHrs, usedCoreHrCol: usedHrs, testCoreHrCol: testHrs})

    return


if __name__ == "__main__":
    main()
