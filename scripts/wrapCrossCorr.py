#!/opt/local/bin/python
#!/Users/grmead/anaconda2/bin/python
#!/usr/bin/env python
# Grant David Meadors
# g r a n t . m e a d o r s @ a e i . m p g . d e
# 02016-07-08 (JD 2457578)
# Wrap call to CrossCorr

import argparse

parser = argparse.ArgumentParser(description='Read in arguments to handle CrossCorr tests')
parser.add_argument('--lalpath',type=str,help='Location of SWIG-wrapped LAL packages (assuming they are within user home directory)',default='/Documents/CrossCorr/LALApps/opt/lalsuite/lib/python2.7/site-packages')
parser.add_argument('--lalbin', type=str,help='Location of executable binary LAL packages (assuming they are within user home directory)', default='/Documents/CrossCorr/LALApps/opt/lalsuite/bin')
parser.add_argument('--sourcerc',type=str,help='Source script for the SWIG-wrapped LAL packages to be added to path (assuming they are within user home directory)',default='/Documents/CrossCorr/LALApps/etc/lalsuiterc')
parser.add_argument('--sft',type=str,help='Location of SFT to load in', default='example.sft')
parser.add_argument('--fmin',type=float,help='Minimum SFT frequency', default=99.0)
parser.add_argument('--fmax',type=float,help='Maximum SFT frequency', default=101.0)
parser.add_argument('--fBand',type=float,help='Width for CrossCorr to search', default=0.001)
parser.add_argument('--dfFstat',type=float,help='F-stat frequency bin spacing', default=1)
parser.add_argument('--earth',type=str,help='Location of earth ephemeris file within directory', default='earth00-19-DE405.dat.gz')
parser.add_argument('--sun',type=str,help='Location of sun ephemeris file within directory', default='sun00-19-DE405.dat.gz')
parser.add_argument('--ephemerisDir',type=str,help='Location of ephemeris directory', default='/Users/grmead/Documents/CrossCorr/LALApps/opt/lalsuite/share/lalpulsar/')
parser.add_argument('--InjF',type=float,help='injection: frequency', default=100.0)
parser.add_argument('--InjAsini',type=float,help='injection: a sin i',default=1.44)
parser.add_argument('--InjAsiniBand',type=float,help='uncertainty injection: a sin i',default=0.27)
parser.add_argument('--InjPeriod',type=float,help='injection: period', default=68023.82)
parser.add_argument('--InjAlpha',type=float,help='injection: alpha', default=4.27569923850)
parser.add_argument('--InjDelta',type=float,help='injection: delta', default=-0.272973858335)
parser.add_argument('--InjRefTime',type=float,help='injection: reftime', default=1245974416.000000000000)
parser.add_argument('--InjEcc',type=float,help='injection: eccentricity', default=0.0)
parser.add_argument('--InjArgp',type=float,help='injection: argument of periapsis', default=0.0)
parser.add_argument('--InjTp',type=float,help='injection: time of periapsis passage', default=1245967532.759551525116)
parser.add_argument('--InjTpBand',type=float,help='injection: uncertainty in time of periapsis passage', default=1125.0)
parser.add_argument('--InjH0',type=float, help='Injected strain', default=1.0e-25)
parser.add_argument('--InjCosi',type=float, help='Inclination angle wrt line of sight', default=0.967247211460)
parser.add_argument('--InjPsi',type=float, help='Polarization angle psi', default=5.711414939419)
parser.add_argument('--InjPhi0',type=float, help='Initial signal phase at reference time', default=4.114621429583)
parser.add_argument('--InjSqrtSX',type=float, help='Detector noise floor to simulate', default=4.0e-24)
parser.add_argument('--mfd',action='store_true', help='Run Makefakedata to generate injection on-the-fly', default=True)
parser.add_argument('--detectorList',type=str, help='Detectors in search, space-separated like "H1 L1"', default="H1,L1")
parser.add_argument('--tstart',type=float, help='Time of start of analysis', default=1245974416.000000000000)
parser.add_argument('--tspan', type=float, help='Total duration to cover, in seconds)', default=3.0e6)
parser.add_argument('--tsft', type=float, help='SFT length of each timestamp, in seconds', default=1800)
parser.add_argument('--toverlap', type=float, help='time to overlap successive SFTs in seconds', default=0.0)
parser.add_argument('--randseed',type=int,help='Random seed to fix injection noise values', default=314)
parser.add_argument('--Fmethod',type=str,help='Method to used for calculating F-stat, e.g., demod or resampling', default='FMETHOD_RESAMP_BEST')
parser.add_argument('--maxLag',type=float,help='Maximum lag time', default=1800)
parser.add_argument('--numBins',type=int,help='Number of bins',default=2)
parser.add_argument('--numCand',type=int,help='Number of candidates to keep',default=10000)
parser.add_argument('--mismatchF',type=float,help='Allowed mismatch in frequency',default=0.1)
parser.add_argument('--mismatchA',type=float,help='Allowed mismatch in a sin i',default=0.1)
parser.add_argument('--mismatchT',type=float,help='Allowed mismatch in time of ascension',default=0.1)
parser.add_argument('--shiftPeriodPhase', type=float, help='Shift TpToAsc by this fraction of a period', default=0.0)
parser.add_argument('--isolatedOnly',action='store_true', help='Ignore binary parameters: test the case of an isolated source', default=False)
parser.add_argument('--signalOnly', action='store_true', help='Test with no noise', default=False)
parser.add_argument('--computeFstatistic', action='store_true', help='Call the above calculation with the external, compiled lalapps_ComputeFstatistic', default=True)
parser.add_argument('--predictFstat', action='store_true', help='Predict the F-statistic using lalapps_PredictFstat', default=False)
parser.add_argument('--MFD', action='store_true', help='Use make-fake-data to generate a signal', default=True)
parser.add_argument('--MFDdataFile', type=str, help='Location for Makefakedata_v5, if needed, to store data', default='H1outSFTs')
parser.add_argument('--MFDwing',type=float, help='Wing size in Hertz for the MFD SFTs, to accomodate Doppler shifts', default=0.0)
parser.add_argument('--injectionFileName', type=str, help='Temporary location to store injection parameters', default='injTest.txt')
parser.add_argument('--outputFstat', type=str, help='File to store lalapps_computeFstatistic output', default='outputFstat.txt')
parser.add_argument('--logFilename', type=str, help='File to store lalapps_crosscorr_v2 output', default='log_crosscorr.txt')
args = parser.parse_args()

# Test the F-statistic functions
import libCallCC as lCCC
lCCC.mainCall(args)


