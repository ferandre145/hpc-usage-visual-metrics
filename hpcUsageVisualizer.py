import sys
import os
import argparse
from turtle import color, forward
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime

'''
Description: Read in hpc usage data from excel file and provide a visualization.
    The goal is to help visualize HPC allocated core hours vs actual core hours used.
    There is an additional metric for core hours used in just testing.

'''

comArgs = argparse.ArgumentParser(
    prog="usageVisual", description="Visualize hpc usage data.")
comArgs.add_argument('-f', '--filepath', type=str)
comArgs.add_argument('-o', '--output', type=str)

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
xFontSize = 12
yFontSize = 16
xAxisFont = 20
yAxisFont = 20
titleFontSize = 24
legendFontSize = 14
plotXSize = 25
plotYSize = 13
plotDPI = 500

filepath = args.filepath
outputFile = args.output


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
        filter

        Parameters:
        df (object): pandas dataframe with the HPC usage data

        return:
        dataframe with extra rows dropped
    '''
    print('Cleaning up data...')

    # cut off rows that aren't for hpc usage (comments, empty lines, etc)
    try:
        removeIndex = df[hpcAccCol].tolist().index('N/A')
        # print(
        #     f"First instance of N/A in HPC account column: {removeIndex}")
        # print('Dropping invalid rows and showing result...')
        df = df.drop(df.index[removeIndex:])
    except:
        print('No empty HPC account values found, continuing to show result...')

    return df


def getColVals(df, colName):
    '''
        Return values of a specifiied column from the dataframe.
        Also further clean up of values if necessary

        Parameters:
        df (object): dataframe of the hpc usage data
        colName (str): name of the column to get values from

        return: 
            list of values in the column
    '''
    colValues = []
    for value in df[colName].tolist():
        if(colName != timePeriodCol and colName != hpcAccCol):
            # print(f'removing non numericals from {value}')
            if value != '' and value != 'N/A':
                colValues.append(int(re.sub('[^0-9]', '', str(value))))
            else:
                colValues.append(0)
        else:
            if 'Cheyenne' in value:
                colValues.append(value+'*')
            else:
                colValues.append(value)

    return colValues


def plotData(dataDict):
    '''
        Description: Gather data from given dictionary and plot graph

        Parameters: 
        dataDict (object): Python dictionary containing the time periods, 
        hpc systems/accounts, allocated hours, used hours, and testing hours.
        keys are the same names as the excel columns
    '''
    print('plotting data...')

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

    # if output location not provided, let user decide in the graph popup
    if not args.output:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    else:
        fig = plt.gcf()
        fig.set_size_inches((plotXSize, plotYSize), forward=False)
        time = getCurrentTime()
        plt.savefig((outputFile+f' - {time}'), dpi=plotDPI)
        print(f'Plot figure saved to ${outputFile}')


def getCurrentTime():
    '''Return current time as a string'''
    currentTime = datetime.now()
    return currentTime.strftime('%b-%d-%Y (%I-%M-%Ss %p)')


def readLogData(filepath):
    '''Read in given excel file and return dataframe'''

    acc = 'Project Report for:'
    reportTime = 'Report Run:'
    reportBeginning = 'Report Period Beginning:'
    machine = 'Machines:'
    initAlloc = 'Initial Allocation in Hours:'
    adjustAlloc = 'Adjusted Allocation:'
    usedCoreHrs = 'Total Core Hours Used:'
    fairShare = 'Project Fair Share:'

    data = []
    # go through each log and retrieve data
    for file in os.listdir(filepath):
        tmpDct = {}
        if file.endswith('.txt') or file.endswith('.log'):
            f = open(filepath+file)
            for line in f:
                if acc in line:
                    tmpDct['acc'] = line[line.find(acc)+len(acc):].strip()
                elif reportTime in line:
                    tmpDct['endTime'] = reformatTime(line[line.find(
                        reportTime)+len(reportTime):].strip())
                elif reportBeginning in line:
                    tmpDct['startTime'] = reformatTime(line[line.find(
                        reportBeginning)+len(reportBeginning):].strip())
                elif machine in line:
                    tmpDct['machineID'] = line[line.find(
                        machine)+len(machine):].strip()
                elif initAlloc in line:
                    tmpDct['initialAlloc'] = line[line.find(
                        initAlloc)+len(initAlloc):].strip().replace(',', '')
                elif adjustAlloc in line:
                    tmpDct['adjustedAlloc'] = line[line.find(
                        adjustAlloc)+len(adjustAlloc):].strip().replace(',', '')
                elif usedCoreHrs in line:
                    tmpDct['usedHrs'] = line[line.find(
                        usedCoreHrs)+len(usedCoreHrs):].strip().replace(',', '')
                elif fairShare in line:
                    tmpDct['fairShare'] = line[line.find(
                        fairShare)+len(fairShare):].strip()
            if(len(tmpDct) == 0):
                print('Empty/invalid log file, skipping...')
            else:
                data.append(tmpDct)
    if(len(data) == 0):
        sys.exit('No data retrieved from log directory. Exiting...')
    return data


def plotLogData(data):
    xlabels = []
    for i in range(len(data)):
        label = data[i]['startTime']+'-'+data[i]['endTime'] + \
            " "+data[i]['machineID']+'/'+data[i]['acc']
        xlabels.append(label)

    barsAlloc = getPlotColVals('adjustedAlloc', data)
    barsUsed = getPlotColVals('usedHrs', data)

    allocSpacing = np.arange(len(barsAlloc))
    usedSpacing = [val + barWidth for val in allocSpacing]

    plt.bar(allocSpacing, barsAlloc, color='green',
            width=barWidth, label='Allocated Hours')
    plt.bar(usedSpacing, barsUsed, color='red',
            width=barWidth, label='Used Hours')

    plt.xlabel('Timeframe & HPC / Account', fontsize=xAxisFont)
    plt.ylabel('Core Hours', fontsize=yAxisFont)
    plt.xticks(
        [r + barWidth for r in range(len(barsAlloc))],  xlabels,  fontsize=xFontSize)
    plt.yticks(fontsize=yFontSize)
    plt.legend(fontsize=legendFontSize)
    plt.title('HPC Core Hour Usage', fontsize=titleFontSize)

    # if output location not provided, let user decide in the graph popup
    if not args.output:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    else:
        fig = plt.gcf()
        fig.set_size_inches((plotXSize, plotYSize), forward=False)
        time = getCurrentTime()
        plt.savefig((outputFile+f' - {time}'), dpi=plotDPI)
        print(f'Plot figure saved to ${outputFile}')

    return


def plotShareData(data):
    '''Plot out fair share values from provided log data'''
    xlabels = []
    for i in range(len(data)):
        label = data[i]['startTime']+'-'+data[i]['endTime'] + \
            " "+data[i]['machineID']+'/'+data[i]['acc']
        xlabels.append(label)

    plt.figure(1)

    fairShareVals = getPlotColVals('fairShare', data, toFloat=True)
    spacing = np.arange(len(fairShareVals))

    plt.bar(spacing, fairShareVals, color='green',
            width=barWidth, label='Fair Share')

    plt.xlabel('Timeframe & HPC / Account', fontsize=xAxisFont)
    plt.ylabel('Fair Share', fontsize=yAxisFont)
    plt.xticks([r+barWidth for r in range(len(fairShareVals))],
               xlabels, fontsize=xFontSize)
    plt.yticks(yFontSize)
    plt.title('HPC Fair Share', fontsize=titleFontSize)

    if not args.output:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    else:
        fig = plt.gcf()
        fig.set_size_inches((plotXSize, plotYSize), forward=False)
        time = getCurrentTime()
        plt.savefig((outputFile+' Fair Share '+f' - {time}'), dpi=plotDPI)
        print(f'Plot figure saved to ${outputFile}')
    return


def getPlotColVals(col, data, toFloat=False):
    '''return a list of the specified column values in the given data'''
    vals = []
    for row in data:
        if toFloat:
            vals.append(float(row[col]))
        else:
            vals.append(int(row[col]))

    return vals


def reformatTime(time):
    '''Take time from logs and return a format for plot labels'''
    newTime = time.split()
    return datetime.strptime(
        f'{newTime[1]} {newTime[2]} {newTime[3]}', '%d %b %Y').strftime('%m/%d/%Y')


def main():

    # pass in excel file otherwise assume log file directory
    if(filepath.endswith('.xlsx')):

        df = readData(filepath)
        df = sanitize(df)

        timePeriods = getColVals(df, timePeriodCol)
        hpcAcc = getColVals(df, hpcAccCol)
        allocHrs = getColVals(df, allocCoreHrCol)
        usedHrs = getColVals(df, usedCoreHrCol)
        testHrs = getColVals(df, testCoreHrCol)

        plotData({timePeriodCol: timePeriods, hpcAccCol: hpcAcc,
                  allocCoreHrCol: allocHrs, usedCoreHrCol: usedHrs, testCoreHrCol: testHrs})
    else:
        logData = readLogData(filepath)
        print(logData)
        plotLogData(logData)
        # plotShareData(logData)

    print('closing...')

    return


if __name__ == "__main__":
    main()
