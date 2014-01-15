import os,sys,glob
import loadgmt,kevent
import ssexyhelp
import MCstat
from optparse import OptionParser
from pylab import *
import mplrc
import numpy as np
from matplotlib.ticker import MultipleLocator

# ----------------------------------------------------------------------
def getStats(data,SpanJobAverage=-1,dim=0):
    ''' Get the average and error of all columns in the data matrix. '''

    #SpanJobAverage tells whether the estimator file contains the Bins
    #column added by the merge scripts during merge of a spanned job
    if ndim(data) > dim:
        numBins  = size(data,dim) 
        if SpanJobAverage != -1:
           dataAve  = sum(data[:,:-1]*data[:,-1][:,newaxis],dim)/(1.0*sum(data[:,-1])) 
           dataErr = std(data[:,:-1],0)/sqrt(len(data[:,0])-1.0) 
        else:
            dataAve  = average(data,dim) 
            bins = MCstat.bin(data) 
            dataErr = amax(bins,axis=0)
        
        
    return dataAve,dataErr

# -----------------------------------------------------------------------------
def getScalarEst(type,ssexy,outName,reduceFlag, skip=0):
    ''' Return the arrays containing the reduced averaged scalar
        estimators in question.'''

    fileNames = ssexy.getFileList(type)
    lAveraged = []
    oldFormat = False
    for i, fname in enumerate(fileNames):
        headers   = ssexyhelp.getHeadersFromFile(fname)
        
        if 'dnT' in headers:
            headers = headers[::2]
            oldFormat = True
            print "Old estimator file format detected"
        if 'Bins' in headers: 
           SpanJobAverage = headers.index('Bins')
           headers.pop(SpanJobAverage) 
        else: 
            SpanJobAverage = -1
        lAveraged += [SpanJobAverage]     

    ave = zeros([len(fileNames),len(headers)],float)
    err = zeros([len(fileNames),len(headers)],float)
    for i,fname in enumerate(fileNames):
        # Compute the averages and error
        data = loadtxt(fname,ndmin=2)[skip:,:]
        if oldFormat:
            data = data[:,::2]
        ave[i,:],err[i,:] = getStats(data,lAveraged[i])
    
    # output the estimator data to disk
    outFile = open('reduce-%s%s.dat' % (type,outName),'w');

    # the headers
    outFile.write('#%15s' % reduceFlag[0])
    for head in headers:
        outFile.write('%16s%16s' % (head,'+/-'))
    outFile.write('\n')

    # the data
    for i,f in enumerate(fileNames):
        outFile.write('%16.8E' % float(ssexy.params[ssexy.id[i]][reduceFlag]))
        for j,h in enumerate(headers):
            outFile.write('%16.8E%16.8E' % (ave[i,j],err[i,j]))
        outFile.write('\n')
    outFile.close()

    return headers,ave,err;


# -----------------------------------------------------------------------------
# Begin Main Program 
# -----------------------------------------------------------------------------
def main():

    # define the mapping between short names and label names 
    shortFlags = ['n','T','N','t','u','V','L']
    parMap = {'n':'Initial Density', 'T':'Temperature', 'N':'Initial Number Particles',
              't':'Imaginary Time Step', 'u':'Chemical Potential', 'V':'Container Volume',
              'L':'Container Length'}


    parser = OptionParser() 
    parser.add_option("-T", "--temperature", dest="T", type="float",
                      help="simulation temperature in Kelvin") 
    parser.add_option("-b", "--beta", dest="B", type="float",
                      help="number of particles") 
    parser.add_option("-v", "--reduce", dest="reduce",
                      choices=['r','x','y','T','b'], 
                      help="variable name for reduction [r,x,y,T,b]") 
    parser.add_option("-r", "--replica", dest = "r",type="int",
                      help="number of replica copies") 
    parser.add_option("-x", "--Lx", dest="x", type="int",
                      help="lattice width") 
    parser.add_option("-y", "--Ly", dest="y", type="int",
                      help="lattice height") 
    parser.add_option("-s", "--skip", dest="skip", type="int",
                      help="number of measurements to skip") 
    parser.add_option("-p", "--plot", action="store_true", dest="plot",
                      help="do we want to produce data plots?") 
    parser.set_defaults(plot=False)
    parser.set_defaults(skip=0)
    (options, args) = parser.parse_args() 

    if (not options.reduce):
        parser.error("need a correct reduce flag (-r,--reduce): [r,x,y,T,b]")
    # parse the command line options and get the reduce flag


    # Check that we are in the correct ensemble
    dataName,outName = ssexyhelp.getWildCardString(options) 
    
    ssexy = ssexyhelp.SSEXYHelp(options)
    ssexy.getSimulationParameters()


    # We first reduce the scalar estimators and output them to disk
    head1,scAve1,scErr1 = getScalarEst('estimator',ssexy,outName,options.reduce)

    if options.plot:
        rcParams.update(mplrc.aps['params'])
        # Get the changing parameter that we are plotting against
        param = []
        for ID in ssexy.id:
            param.append(float(ssexy.params[ID][reduceFlag[1]]))
        colors = ["#66CAAE", "#CF6BDD", "#E27844", "#7ACF57", "#92A1D6", "#E17597", "#C1B546",'b']

        figure(1,(8,6))
        connect('key_press_event',kevent.press)
        ax = subplot(111)
        xlabel(r'$\mathrm{L[\AA]}$')
        ylabel(r'$\mathrm{\rho_s/ \rho_{c}}$')
        legend(loc='best',frameon=False)
        tight_layout()
        show()

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__": 
    main()
