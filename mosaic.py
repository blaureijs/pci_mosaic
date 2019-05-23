#======================================================================# 
# Script Name:	mosaic.py
# Author:	Brian Laureijs
# Purpose:      Convert, correct, and mosaic Sentinel-2 imagery
# Assignment: 	ADIP Assn #2 (COGS, Feb 2019)
# Date:         20190203
# Disclaimer:   Completed for fulfilment of academic assessment.
#               Not for distribution. Requires PCI Geomatica.
#======================================================================# 
# Import Libraries                  # Requirements:
#======================================================================# 
import os,shutil                    # Directory and file manipulation
from pci.fimport import *           # Import to pix format
from pci.masking import *           # Cloud/water mask prep
from pci.atcor import *             # Atmospheric correction
from pci.hazerem import *           # Haze removal
from pci.automos import *           # Mosaicking
from pci.str import str as stretch  # Linear enhancement
from pci.lut import *               # Apply look up table
from pci.fexport import *           # Export to tif format

#----------------------------------------------------------------------# 
# Declare global variables
#----------------------------------------------------------------------#  
global sen2                         # Sensor name used in pci correction
sen2="Sentinel-2"                   # functions.
global pixfiles                     # Initialize list of converted pix
pixfiles = []                       # format images.

#----------------------------------------------------------------------# 
# Initialize Paths
#----------------------------------------------------------------------#  
workingdir = r'D:\Mosaic'                       # Main directory
indir = os.path.join(workingdir,"input")        # Raw S2 input
corrdir = os.path.join(workingdir,"corrected")  # Corrected pix output
pixdir = os.path.join(workingdir,"pix")         # Uncorrected pix output
mosdir = os.path.join(workingdir,"mosaic")      # Mosaic output

#----------------------------------------------------------------------#
# Define readtopix() function
#   1. Read folders from input directory to list
#   2. Append XML and band resolution so PCI can read input
#   3. Read Sentinel-2 files to Pix format
#   4. Append pix files to list
#----------------------------------------------------------------------# 
def readtopix(indir):
    infiles = os.listdir(indir)             # List input folders
    for i in range (len(infiles)):          # Add path for 10m S2 Bands
        infiles[i] = "input/" + infiles[i] + "/MTD_MSIL1C.xml?r=%3ABand+Resolution%3A10M"
        pix = "pix/tile" + str(i) + ".pix"  # Name converted pix output
        pixfiles.append(pix)                # Add to list of pix files
        fili=infiles[i]
        print "\tStarting pix conversion file %s" %str(i)
        fimport(fili,pix)                   # Run import function
        print "\tPix conversion completed for %s:" %infiles[i]
        print "\tOutput to %s" %pix

#----------------------------------------------------------------------#
# Define correction() function
#   1. Process masks for raw pix image
#   2. Process haze removal for pix image
#   3. Process atmospheric correction for pix image
#----------------------------------------------------------------------# 
def correction(piximage,hazeout,atcorout):
    print "-"*50
    print "\tProcessing masks..."
    masking( fili       =piximage           # Input pix
            ,asensor    =sen2               # Sentinel-2
            ,hazecov    =[70]               # Haze coverage
            ,clthresh   =[17,22,1]          # Cloud reflectance threshold
            ,filo       =piximage)          # Output (same file)
    print "\tMasks for %s completed" %(piximage)
    print "\tProcessing haze removal... (This may take a while)"
    hazerem( fili       =piximage           # Input pix
             ,asensor   =sen2               # Sentinel-2
             ,maskfili  =piximage           # Masks in same file
             ,maskseg   =[2,3,4]            # Mask channels
             ,hazecov   =[50]               # Haze coverage
             ,filo      =hazeout)           # Output pix
    print "\tHaze removed from %s." %(piximage)
    print "\tProcessing atmospheric correction..."
    atcor(  fili        =hazeout            # Haze corrected input
            ,asensor    =sen2               # Sentinel-2
            ,maskfili   =piximage           # Mask file
            ,atmdef     = "Maritime"        # Atmosphere type
            ,atmcond    = "subarctic"       # Atmosphere conditons
            ,outunits   = "Scaled_Reflectance,10.00" # Output
            ,filo       =atcorout)          # Corrected pix
    print "\t%s atmospheric correction completed." %(piximage)

#----------------------------------------------------------------------#
# Define enhance() function
#   1. Generate a linear stretch LUT for mosaicked pix
#   2. Apply LUT enhancement to pix mosaic
#----------------------------------------------------------------------# 
def enhance(mosin,mosout):
    print "\tGenerating look-up table for enhancement..."
    stretch( file=mosin
            ,dbic=[4]                       # Stretch band 4
            ,dblut=[]
            ,dbsn="LinLUT"
            ,dbsd="Linear Stretch"
            ,expo=[1] )                     # Linear stretch
    stretch( file=mosin
            ,dbic=[3]                       # Stretch band 3
            ,dblut=[]
            ,dbsn="LinLUT"
            ,dbsd="Linear Stretch"
            ,expo=[1] )                     # Linear stretch
    stretch( file=mosin
            ,dbic=[2]                       # Stretch band 2
            ,dblut=[]
            ,dbsn="LinLUT"
            ,dbsd="Linear Stretch"
            ,expo=[1] )                     # Linear stretch
    print "\tLUT generation complete."
    print "\tApplying enhancement..."
    lut(    fili=mosin
            ,dbic=[4,3,2]                   # Use bands (4,3,2)
            ,dblut=[4,3,2]                  # LUT segments
            ,filo=mosout                    # Output mosaic
            ,datatype="16U"                 # 16-bit unsigned
            ,ftype="PIX" )                  # Pix output
    print "\tMosaic enhancement complete."

#----------------------------------------------------------------------#
# Define mainline function
#   1. Clear directories if they already exist
#   2. Read input to pix format
#   3. Process haze removal and atmospheric correction
#   4. Move corrected pix to corrrected dir
#   5. Mosaic corrected images
#   6. Enhance mosaic
#   7. Export enhanced image to TIF format for use with ArcGIS
#----------------------------------------------------------------------#
def main():
    if os.path.isdir(indir)==False:
        print "\tMissing input folder!"
        print "\tAdd unzipped input files to input folder"
    if os.path.isdir(corrdir)==True:
        print "\tClearing corrected folder"
        shutil.rmtree(corrdir)              # Delete \corrected
        os.mkdir(corrdir)                   # Create \corrected
    else:
        os.mkdir(corrdir)                   # Create \corrected
    if os.path.isdir(pixdir)==True:
        print "\tClearing pix folder"
        shutil.rmtree(pixdir)               # Delete \pix
        os.mkdir(pixdir)                    # Create \pix
    else:
        os.mkdir(pixdir)                    # Create \pix
        
    if os.path.isdir(mosdir)==True:
        print "\tClearing mosaic folder"
        shutil.rmtree(mosdir)               # Delete \mosaic
        os.mkdir(mosdir)                    # Create \mosaic
    else:
        os.mkdir(mosdir)                    # Create \mosaic
    print "-"*22+"Step 1"+"-"*22    
    readtopix(indir)                        # Convert raw input to pix
    print "-"*22+"Step 2"+"-"*22    
    for i in range(len(pixfiles)):
        hazeoutput =  pixfiles[i][:9] + "_hzrm.pix"
        atcoroutput = pixfiles[i][:9] + "_atcor.pix"
        correction(pixfiles[i],hazeoutput,atcoroutput)  # Correction
        shutil.move(atcoroutput,corrdir)    # Move corrected output
        print "\tCorrected %s." %pixfiles[i]
        print "\tCorrected file moved to %s." %corrdir
    print "-"*22+"Step 3"+"-"*22
    print "\tStarting Mosaicking process ..."
    automos(    mfile="/corrected"          # Mosaic files in \corrected
                ,mostype="FULL"             # Full format mosaic
                ,filo="mosaic/mosaic_out.pix"   # Output file
                ,ftype="PIX"                # Output to pix
                ,radiocor="NONE"            # No radiometric corr.
                ,balmthd="NONE"             # No balancing
                ,cutmthd="MINDIFF"          # Minimum difference cut method
                ,filvout="mosaic/cutlines.shp") # Output cutlines
    print "\tMosaicking process completed."
    print "-"*22+"Step 4"+"-"*22
    enhance("mosaic/mosaic_out.pix","mosaic/mosaic_enhanced.pix")            
    print "-"*22+"Step 5"+"-"*22
    print "\tExporting Mosaic to TIF format..."
    fexport( fili="mosaic/mosaic_enhanced.pix"  # Input pix
             ,filo="mosaic/mosaic_enhanced.tif" # Output tif
             ,dbic=[1,2,3]                      # Channels
             ,ftype="TIF" )
    print "\tFormat conversion complete."
    print "\tThe Mosaicking script has finished running."
    print "="*50


#----------------------------------------------------------------------#
# Mainline
#   - Loop to stop script from autorunning if user is unaware of file
#     deletion at beginning of script.
#----------------------------------------------------------------------#

print "="*50                                    # Header
print "Sentinel-2 Mosaicking Script"
print "="*50

print "\tThis script should be run from %s" %workingdir
print "\tUnzip Sentinel-2 input to %s" %indir
print "\tRunning this script will DELETE existing data"
print "\tfrom corrected, mosaic, and pix folders!"
start = raw_input("\tContinue? (Y/N):")
while start[0].upper() <> "N":                  # Start a loop
    if len(start) == 0:                         # Stop if no answer
        start = "N"                             # Exit script
        print " ----- Goodbye"*2, "-----"         
    elif start[0].upper() == "Y":               # Start if starts with y
        main()                                  # Run main()
    else:
        start = "N"                             # Kill loop
        print " ----- Goodbye"*2, "-----"       # Exit script
