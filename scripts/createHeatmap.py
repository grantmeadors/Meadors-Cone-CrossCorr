#!/usr/bin/env python
import math, os, commands, shutil, sys, re
import matplotlib as matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.backends.backend_agg
import numpy as np
import argparse

# Summarize the CrossCorr toplist
# 02016-07-19 (JD 2457589)
# g r a n t . m e a d o r s @ a e i . m p g . d e
# usage: ./createHeatmap.py

parser = argparse.ArgumentParser(description='Summarize the output files of a given Sco X-1 MDC data set')
parser.add_argument('--nameToplist',type=str, help = 'Name of toplist', default= 'toplist_crosscorr.dat')
parser.add_argument('--fCenter',type=float, help='Use center(frequency in Hertz)', default=100.0)
parser.add_argument('--fBand',type=float, help='Use center(frequency in Hertz)', default=0.001)
parser.add_argument('--bypassSummary',action='store_true', help='Avoid regenerating the summary file, useful if already made')
parser.add_argument('--band',action='store_true', help='Use with 1 Hz templateSearch band, or standalone: make plots appropriate for a 5 Hz band')
parser.add_argument('--elsewhere', help='Path to directory containing the output files')
parser.add_argument('--massiveSummary',action='store_true', help='Deal with large output directories')
parser.add_argument('--plotSkyContour',type=float, help='Plot a circle around this point in the sky: two arguments, alpha and delta in radians', nargs=2)
parser.add_argument('--noiseTest',action='store_true', help='Make histrogram noise plots')
parser.add_argument('--templateSearch',action='store_true', help='Change commands in way needed for templateSearch')
parser.add_argument('--multiTemplateSearch',type=str, help='use instead of --templateSearch, specify number of bands in output directory')
parser.add_argument('--closed',action='store_true', help='Can be used, especially with --multiTemplateSearch, for working with closed pulsars')
parser.add_argument('--skipPlotH0',action='store_true',help='Use to skip plotting h0 in a given band, if desired for  memory or speed.',default=False)
parser.add_argument('--colorMap',type=str,help='Colormap option for plots; jet is default for web, Greys better for papers',default='jet')
parser.add_argument('--texMode',action='store_true',help='Avoids plotting the head title, so as to fit many journal styles. Invokes the rc families for nice plots',default=False)
parser.add_argument('--plot',action='store_true',help='Generate the plots',default=True)
parser.add_argument('--FA',action='store_true', help='Plot the F-A plane', default=True)
parser.add_argument('--TF',action='store_true', help='Plot the T-F plane', default=False)
parser.add_argument('--AT',action='store_true', help='Plot the A-T plane', default=False)
parser.add_argument('--dFnotA',action='store_true', help='Plot dF instead of a sin i', default=False)
parser.add_argument('--FIndex',type=int, help='F index value to use for A-T plots', default=0)
parser.add_argument('--AIndex',type=int, help='A index value to use for T-F plots', default=0)
parser.add_argument('--TIndex',type=int, help='T index value to use for F-A plots', default=0)
parser.add_argument('--threeD', action='store_true', help='Attempt 3D plot -- currently useless', default=False)
args = parser.parse_args()

def summarizer(args):
    headJobName = args.nameToplist
    verboseSummaryFile = 'verbose_summary-' + str(args.fCenter) +'.txt'

    if args.bypassSummary:
        print 'Bypassing summary file creation'

    os.system('cat ' + headJobName + ' > ' + verboseSummaryFile)
    
    # Defined by 'print_crossCorrBinaryline_to_str' in CrossCorrToplist.c
    # Not by the CrossCorrBinaryOutputEntry struct in CrossCorrToplist, h, confusingly
    dataDTypes = np.dtype({'names':['freq','tp','argp','asini','ecc','period','estSens','evSquared','rho'],'formats':['f8','f8','f8','f8','f8','f8','f8','f8','f8']}) 
    verboseData = np.loadtxt(verboseSummaryFile,dtype=dataDTypes)

    fArray = verboseData['freq']
    asiniArray = verboseData['asini']
    pArray = verboseData['period']
    if args.dFnotA:
        dfArray = 2 * np.pi * fArray * asiniArray / pArray
        modArray = dfArray
    else:
        modArray = asiniArray
    tpArray = verboseData['tp']
    RArray = verboseData['rho']
    ESArray = verboseData['estSens']
  
    # Note, we now have to deal with three-dimensionality
    # For now, just make it two-dimensional with a command such as
    # ./wrapCrossCorr.py --InjTpBand 0.001
    # in ../example/

    if (args.plot):

        # The most confusing question is how to flip axes
        # Reshaping, we realize quickly enough, depends on
        # the layout of the data, which as noted elsewhere
        # is listed f, t, a in the toplist
        # We later remove one axes from this ordering
        # Plotting (f, a), without t, the ordered entries
        # are still in the right order (flipAxes = 0), but
        # plotting (a, t), or (t, f), we have to reverse
        # the order from the toplist (flipAxes = 1)
        # Also, takeAxisIndex seems to run backwards from the
        # (f, t, a) order: that is because a transpose is taken
        # immediately after reshaping, yielding (a, t, f) order.
        # We do this transpose to comply with pyplot.imshow 
        if args.TF:
            xArray = tpArray
            yArray = fArray
            zArray = modArray
            zIndex = args.AIndex
            takeAxisIndex = 0
            flipAxes = 1
        elif args.AT:
            xArray = modArray
            yArray = tpArray
            zArray = fArray
            zIndex = args.FIndex
            takeAxisIndex = 2
            flipAxes = 1
        elif args.FA:
            xArray = fArray
            yArray = modArray
            zArray = tpArray
            zIndex = args.TIndex
            takeAxisIndex = 1
            flipAxes = 0
        else:
            print 'Incompatible options'
      
        # In the toplist, columns change from the right (big-endian)
        # They are listed f, t, a,
        # Python reads in entries in the order f0t0a0, f0t0a1, f0t1a0,...
        FLen = len(np.unique(fArray))
        TLen = len(np.unique(tpArray))
        ALen = len(np.unique(modArray))
        

        if args.dFnotA:
            modLabel = 'Modulation depth: df (Hz)'
            # This override is necessary because the
            # df are, for it, all unique. However, this makes it tricky because
            # the graph really is skewed
            ALen = len(np.unique(asiniArray))            
        else:
            modLabel = 'Projected semi-major axis (light-s)'


        if args.TF:
            print 'T-F plot'
            figXLabel = 'Periapsis time: tp (s)'
            figYLabel = 'Frequency: f (Hz)'
            graphHead = 'TF'
        elif args.AT:
            print 'A-T plot'
            figXLabel = modLabel
            figYLabel = 'Periapsis time: tp (s)'
            graphHead = 'AT'
        elif args.FA:
            print 'F-A plot'
            figXLabel = 'Frequency: f (Hz)'
            figYLabel = modLabel
            graphHead = 'FA'
        else:
            print 'Incompatible options'


        xShaped3D = np.reshape(xArray, (FLen, TLen, ALen)).T
        yShaped3D = np.reshape(yArray, (FLen, TLen, ALen)).T
        zShaped3D = np.reshape(zArray, (FLen, TLen, ALen)).T

  
        print 'Number of bins in data arrays (F,T,A): ' + str(xShaped3D.T.shape)
        ESShaped3D = np.reshape(ESArray, (FLen, TLen, ALen)).T
        RShaped3D = np.reshape(RArray, (FLen, TLen, ALen)).T


        # Reduce to 2D
        xShaped = takeAxisAndRotate(xShaped3D, zIndex, takeAxisIndex, flipAxes)
        yShaped = takeAxisAndRotate(yShaped3D, zIndex, takeAxisIndex, flipAxes)
        ESShaped = takeAxisAndRotate(ESShaped3D, zIndex, takeAxisIndex, flipAxes)
        RShaped = takeAxisAndRotate(RShaped3D, zIndex, takeAxisIndex, flipAxes)


        #x, y = np.meshgrid(xShaped[0, :], yShaped[:, 0])
        extensions = [xShaped[0, 0], xShaped[-1, -1], yShaped[0, 0], yShaped[-1, -1]]

      
        ESCenter = ESShaped.max()
        RCenter = RShaped.max()
        centerString = 'maximum value: '


        centerESSpotX = str(xShaped.compress((ESShaped == ESCenter).flat)[0])
        centerESSpotY = str(yShaped.compress((ESShaped == ESCenter).flat)[0])
        centerRSpotX = str(xShaped.compress((RShaped == RCenter).flat)[0])
        centerRSpotY = str(yShaped.compress((RShaped == RCenter).flat)[0])

        pulsarName = "band-" + str(args.fCenter)

        #plotImshow(args, 'ES', 'estSens', xArray, yArray, ESShaped, xShaped, yShaped, graphHead, pulsarName, figXLabel, figYLabel, ESCenter, centerESSpotX, centerESSpotY, centerString, extensions)
        plotImshow(args, 'R', 'Rho statistic', xArray, yArray, RShaped, xShaped, yShaped, graphHead, pulsarName, figXLabel, figYLabel, RCenter, centerRSpotX, centerRSpotY, centerString, extensions) 

def plotImshow(args, graphKind, graphKindLong, xArray, yArray, shaped, xShaped, yShaped, graphHead, pulsarName, figXLabel, figYLabel, center, centerSpotX, centerSpotY, centerString, extensions):
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        if (args.threeD == True):
             ax.plot(xArray,yArray)
        else:
             paramSpacePixelMap = ax.imshow(shaped, origin = 'lower', \
             interpolation = 'nearest', extent = extensions, cmap = args.colorMap)
             paramSpacePixelMap = fig.colorbar(paramSpacePixelMap, shrink = 0.5, extend = 'both')
             #print 'Skipping grid lines'
        ax.set_aspect('auto')
        ax.set_xlabel(figXLabel)
        ax.set_ylabel(figYLabel)
        ax.set_title(' ' + graphKindLong + \
        ' vs parameters for band centered ' + str(args.fCenter) + ' Hz at '  + ' \n \
        ' + centerString + str(center) + ' at (x, y) = (' + centerSpotX +', ' + centerSpotY + ') \n \
        Number of bins in data arrays (x, y): ' + str(xShaped.T.shape) + ' \n \
        ')
        if args.texMode:
            print 'SHOULD BE Skipping title to conform with journal style'
        if args.texMode:
            plt.savefig(graphHead + 'results' + graphKind + '-' + pulsarName + '.eps', format='eps', dpi=720, bbox_inches='tight')
        plt.savefig(graphHead + 'results' + graphKind + '-' + pulsarName + '.png')
        plt.savefig(graphHead + 'results' + graphKind + '-' + pulsarName + '.pdf')
        plt.close()
        plt.clf()

def takeAxisAndRotate(threeDarray, zIndex, takeAxisIndex, flipAxes):
    firstTwoDarray = np.take(threeDarray, zIndex, takeAxisIndex)
    if (flipAxes == 1):
        twoDarray = firstTwoDarray.T
    elif (flipAxes == 0):
        twoDarray = firstTwoDarray
    else:
        'flipAxes not configured correctly'
    return twoDarray
   
 
# Check plotting families
if args.texMode:
    from matplotlib import rc
    rc('font', **{'family':'serif','serif':['Times']})
    rc('text',usetex=True)
        
summarizer(args)
