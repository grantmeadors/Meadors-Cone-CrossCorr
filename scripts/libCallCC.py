# Grant David Meadors
# g r a n t . m e a d o r s @ a e i . m p g . d e
# 02016-07-08 (JD 2457578)
# Support functions for calling CrossCorr

import os, sys

def mainCall(args):
    userhome = os.getenv('HOME')
    lalswigpath = userhome + args.lalpath
    lalbinpath = userhome + args.lalbin
    
    if lalswigpath in sys.path:
        print 'SWIG wrappings appear to be installed; location:'
        print lalswigpath
        lalbinpath = lalbinpath + '/'
        import lalpulsar as lp
        if args.MFD:
            print 'Using lalapps_Makefakedata_v5...'
            invokeMakefakedata(lp, args, lalbinpath)
        print 'Using lalapps_CrossCorr_v2...'
        invokeCrossCorr(lp, args, lalbinpath)
    else:        
        print 'Note: SWIG wrappings do not appear to be in path'
        print 'For more precise investigation, SWIG may be helpful. Expected location, '
        print 'source ' + userhome + args.sourcerc
        lp = ''
        lalbinpath = ''
        if args.MFD:
            invokeMakefakedata(lp, args, lalbinpath)
        invokeCrossCorr(lp, args, lalbinpath)
    
def invokeMakefakedata(lp, args, lalbinpath):
    from subprocess import call
 
    compiledMakefakedata = lalbinpath + 'lalapps_Makefakedata_v5'
    print compiledMakefakedata

    injectionsMakefakedata = \
    "Alpha = " + str(args.InjAlpha) + '\n'\
    "Delta = " + str(args.InjDelta) + '\n'\
    "refTime = " + str(args.InjRefTime) + '\n'\
    "Freq = " + str(args.InjF) + '\n'\
    "h0 = " + str(args.InjH0) + '\n'\
    "cosi = " + str(args.InjCosi) + '\n'\
    "psi = " + str(args.InjPsi) + '\n'\
    "phi0 = " + str(args.InjPhi0) + '\n'
    if args.isolatedOnly:
        print 'Ignoring binary parameters: testing as ISOLATED source'
    else:
        injectionsMakefakedata = injectionsMakefakedata + \
        "orbitasini = " + str(args.InjAsini) + '\n'\
        "orbitEcc = " + str(args.InjEcc) + '\n'\
        "orbitTp = " + str(args.InjTp) + '\n'\
        "orbitPeriod = " + str(args.InjPeriod) + '\n'\
        "orbitArgp = " + str(args.InjArgp)
    fid = open(args.injectionFileName, 'w')
    fid.write(injectionsMakefakedata)
    fid.close()

    try:
        os.makedirs(str(args.MFDdataFile))
    except OSError:
        if not os.path.isdir(str(args.MFDdataFile)):
            raise

    argsMakefakedata = \
    " --injectionSources " + str(args.injectionFileName) + \
    " --startTime " + str(args.tstart) + \
    " --duration " + str(int(args.tspan)) + \
    " -I " + '"' + str(args.detectorList) + '"' + \
    " --fmin " + str(args.fmin - args.MFDwing) + \
    " --Band " + str(args.fmax - args.fmin + 2.0*args.MFDwing) + \
    " --Tsft " + str(args.tsft) + \
    " --SFToverlap " + str(args.toverlap) + \
    " -n " + str(args.MFDdataFile) + \
    " -s " + \
    " --sqrtSX " + str(args.InjSqrtSX) + \
    " --randSeed " + str('314')

    print 'ARGUMENTS (Makefakedata_v5):'
    print argsMakefakedata
    call(compiledMakefakedata + argsMakefakedata, shell=True) 


def invokeCrossCorr(lp, args, lalbinpath):
    from subprocess import call    

    print 'Submitting arguments to compiled version of lalapps_ComputeFstatistic_v2:'
    compiledCrossCorr = lalbinpath + 'lalapps_pulsar_crosscorr_v2'
    print compiledCrossCorr

    if args.MFD:
        sftLocation = args.MFDdataFile
    else:
        sftLocation = args.sft

    # Allow the addition of fractional orbital period for study
    orbPhaseShifter = args.shiftPeriodPhase*float(args.InjPeriod)
 
    argsCrossCorr = \
    " --logFilename " + str(args.logFilename) + \
    " --alphaRad " + str(args.InjAlpha) + \
    " --deltaRad " + str(args.InjDelta) + \
    " --fStart " + str(float(args.InjF) - float(args.fBand)/2.0) + \
    " --fBand " + str(args.fBand) + \
    " --numBins " + str(args.numBins) + \
    " --numCand " + str(args.numCand) + \
    " --mismatchF " + str(args.mismatchF) + \
    " --mismatchA " + str(args.mismatchA) + \
    " --mismatchT " + str(args.mismatchT) + \
    " --refTime " + str(args.InjRefTime) + \
    " --sftLocation " + "'" + str(sftLocation) + '/*.sft' + "'" + \
    " --orbitAsiniSec " + str(float(args.InjAsini) - float(args.InjAsiniBand)/2.0) + \
    " --orbitAsiniSecBand " + str(args.InjAsiniBand) + \
    " --orbitPSec " + str(args.InjPeriod) + \
    " --orbitTimeAsc " + str(float(args.InjTp) - float(args.InjTpBand)/2.0 + orbPhaseShifter) + \
    " --orbitTimeAscBand " + str(args.InjTpBand) + \
    " --maxLag " + str(args.maxLag) + \
    " --startTime " + str(int(args.tstart)) + \
    " --endTime " + str(int(args.tstart + args.tspan)) + \
    ""
    #" --dFreq " + str(args.dfFstat)

    print 'ARGUMENTS (CrossCorr):'
    print argsCrossCorr
    call(compiledCrossCorr + argsCrossCorr, shell=True)
