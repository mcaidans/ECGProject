import wfdb
import pandas as pd
import numpy as np
import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import matplotlib.pyplot as plt

#HyperParameters
SecondsWanted = 30 #Seconds of data wanted

#Global Variables
sampSize = int(SecondsWanted*360) #Sets sample size to number of seconds by Hz(360)
sampIncrement = 1/360
annotationArray = np.empty((0,4), int)
signalArray = np.empty((0,2), int)

#Initially read data in
def readData(filename):
    global annotationArray
    global signalArray
    #read in data using
    record = wfdb.rdsamp(filename, sampto = sampSize)
    annotation = wfdb.rdann(filename, 'atr', sampto = sampSize)
    sig, fields = wfdb.srdsamp(filename, sampto = sampSize)

    #read record and signal into an array

    for i in range(0, len(sig)):
        signalArray = np.append(signalArray, np.array([[float("{0:.3f}".format(i*sampIncrement)), sig[i][0]]]), axis=0)

    #read annotations into array

    for i in range(0, len(annotation.annsamp)):
        annotationArray = np.append(annotationArray, np.array([[annotation.annsamp[i], float("{0:.3f}".format(annotation.annsamp[i]/360)), float("{0:.3f}".format(signalArray[:,1][annotation.annsamp[i]])), annotation.anntype[i]]]), axis=0)

#Save signals to CSV file
def saveSignalToFile():
    #Save signal into CSV file
    np.savetxt("signal.csv", signalArray, fmt='%.3f', delimiter=",", header="MLII", comments="elapsed_time,")

#INCOMPLETE Save Annotations to file
def saveAnnoToFile():
    #Read annotations into array and save to file
    #annotationFile = open('annotations.txt', 'w')
    annotationArray = []
    for i in range(0, len(annotation.annsamp)):
        annotationArray.append([annotation.annsamp[i], annotation.anntype[i]])
        #annotationFile.write('{} {}\n'.format("%s" % annotationArray[i][0], annotationArray[i][1]))

#Plot Entire graph and save as image
def plotWholeGraphImage():
    plt.plot(signalArray[:,0], signalArray[:,1])
    plt.savefig("Full.png")

#Plot entire graph and open in browser interactively
def plotWholeGraphBrowser():
    trace0 = go.Scatter(
                      #x = df['elapsed_time'], y = df['MLII'],
                       #x = signalArray[:,0], y = signalArray[:,1],
                       #x = outputArray[:,0], y = outputArray[:,1],
                       x = outputArray[0][:,0], y = outputArray[0][:,1],
                      name='MLII'
                      )
    '''
    trace1 = go.Scatter(
                      x = annotationArray[:,1], y = annotationArray[:,2],
                      mode='markers',
                      name='annotations'
                      )
    '''
    layout = go.Layout(
                      title='MLII',
                      plot_bgcolor='rgb(230, 230,230)',
                      showlegend=True
                      )
    #fig = go.Figure(data=[trace0, trace1], layout=layout)
    fig = go.Figure(data=[trace0], layout=layout)

    plotly.offline.plot(fig, filename='temp-plot.html', validate=False)
    #auto_open=True, image = 'png', image_filename='plot_image', output_type='file', image_width=800, image_height=600,

#support function to check annotation accuracy
def checkAnno(i):
    if (i != 0) and (i != len(signalArray[:,1])-1):         #if not first or last
        if signalArray[i-1][1] > signalArray[i][1]:         #check if before is larger than current
            if signalArray[i][1] > signalArray[i+1][1]:   #check if before larger than after
                return checkAnno(i-1)                                           #recursion check value before
            else:                                                           #else if after is larger than before
                return checkAnno(i+1)                                          #recursion cfheck after
        elif signalArray[i+1][1] > signalArray[i][1]:           #check if after larger than current
            return checkAnno(i+1)
        else:
            return i
    elif i == 0:
        if signalArray[i+1][1] > signalArray[i][1]:
            return checkAnno(i+1)
        else:
            return i
    else:
        if signalArray[i-1][1] > signalArray[i][1]:
            return checkAnno(i-1)
        else:
            return i

#function to correct annotation accuracy
def correctAnno():
    for i in range(0, len(annotationArray[:,1])):
        index = checkAnno(int(annotationArray[i][0]))
        annotationArray[i][0] = index
        annotationArray[i][1] = signalArray[index][0]
        annotationArray[i][2] = signalArray[index][1]

#Calculates average RR interval
def calculateOutput():
    y = annotationArray[:,0].astype(np.int)
    #return np.diff(y)                    #get full diff
    return int(np.average(np.diff(y))/2) #get half of diff

#Outputs heartbeats individually as images
def outputDataAsImage():
    outputSize = calculateOutput()
    allOutputArray = []
    for i in range(0, len(annotationArray[:,0])):
        if (int(annotationArray[:,0][i]) - outputSize) >=0 and (int(annotationArray[:,0][i]) + outputSize) < len(signalArray): #checking if outofbounds
            outputArray = np.empty((0,2), int)
            for j in range(0-outputSize, outputSize):
                #print(int(annotationArray[:,0][i])+j)
                outputArray = np.append(outputArray, np.array([[signalArray[int(annotationArray[:,0][i])+j][0], signalArray[int(annotationArray[:,0][i])+j][1]]]), axis=0)
            allOutputArray.append(outputArray)
    for i in range(0, len(allOutputArray)):
        plt.plot(allOutputArray[i][:,0], allOutputArray[i][:,1])
        plt.savefig("output/100_%s.png" % i)
        plt.close()

#Outputs heartbeats individually as 1D arrays
def outputDataAs1dArray():
    outputSize = calculateOutput()
    allOutputArray = []
    for i in range(0, len(annotationArray[:,0])):
        if (int(annotationArray[:,0][i]) - outputSize) >=0 and (int(annotationArray[:,0][i]) + outputSize) < len(signalArray): #checking if outofbounds
            outputArray = []
            for j in range(0-outputSize, outputSize):
                outputArray.append(signalArray[int(annotationArray[:,0][i])+j][1])
            allOutputArray.append(outputArray)
    return allOutputArray

readData('mitdb/100')   #read data in
correctAnno()           #correct annotations
outputArray = outputDataAs1dArray() #get data as array of 1d arrays
