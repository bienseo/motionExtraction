#!/Users/admin/anaconda/bin/python

import textwrap
import dicom
import re
import os
import sys
import argparse


# In[83]:
def getDicomInfo(directory):
    '''
    Input : directory location
    Output : dicom information
    '''
    #Looping through the input directory
    search=True

    while search:
        for root, dirs, files in os.walk(directory):
            if re.search('REST$',root):
                #Looping through the bunch of files
                for singleFile in files:
                    #if there is dicom files
                    if re.search('.*ima|.*dcm',singleFile,flags=re.IGNORECASE):
                        return os.path.join('root',singleFile)

def dcm2nii(firstDicomFile,directory):

def to3d(firstDicomFile):
    command = 'to3d -prefix {outputLocation} -tpattern alt+z'

def main(args):
    #get first dicom file of the REST directory
    firstDicomFile=getDicomInfo(args.foldername)


def motionExtraction(directory):

if __name__=='__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
            description = textwrap.dedent('''\
                    {codeName} : Returns motion parameters extracted from dicom within the directory
                    ====================
                        eg) {codeName}
                        eg) {codeName} --dir /Users/kevin/NOR04_CKI
                    '''.format(codeName=os.path.basename(__file__))))

            #epilog="By Kevin, 26th May 2014")
    parser.add_argument('-dir','--directory',help='Data directory location, default = pwd',default=os.getcwd())
    parser.add_argument('-F','--foldername',default='REST',help='Print all information')
    args = parser.parse_args()
    main(args)




def main(args):

    firstDicomFile = getDicomInfo(args.directory)

    try:
        if args.all:
            print firstDicomFile
        if args.name:
            print firstDicomFile.PatientName
        if args.id:
            print firstDicomFile.PatientID
        if args.sex:
            print firstDicomFile.PatientSex
        if args.dob:
            print firstDicomFile.PatientBirthDate
        if args.date:
            print firstDicomFile.StudyDate

    except:
        #print re.findall('\x08\x00(\d{8})\x10\x00',' '.join(firstDicomFile.MediaStorageSOPClassUID[5])),
        #print re.findall('\x08\x00(\d{8})\x10\x00',' '.join(firstDicomFile.MediaStorageSOPClassUID[6]))

        four = re.findall('\x08\x00(\d{8})\x10\x00',firstDicomFile.MediaStorageSOPClassUID[4])
        five = re.findall('\x08\x00(\d{8})\x10\x00',firstDicomFile.MediaStorageSOPClassUID[5])
        six = re.findall('\x08\x00(\d{8})\x10\x00',firstDicomFile.MediaStorageSOPClassUID[6])

        if four != []:
            print four
        elif five != []:
            print five
        else:
            print six



if __name__=='__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
            description = textwrap.dedent('''\
                    {codeName} : Returns information extracted from dicom within the directory
                    ====================
                        eg) {codeName}
                        eg) {codeName} --dir /Users/kevin/NOR04_CKI
                    '''.format(codeName=os.path.basename(__file__))))

            #epilog="By Kevin, 26th May 2014")
    parser.add_argument('-dir','--directory',help='Data directory location, default = pwd',default=os.getcwd())
    parser.add_argument('-n','--name',action='store_true',help='Get patient name')
    parser.add_argument('-i','--id',action='store_true',help='Get patient ID')
    parser.add_argument('-s','--sex',action='store_true',help='Get patient sex')
    parser.add_argument('-b','--dob',action='store_true',help='Get patient DOB')
    parser.add_argument('-d','--date',action='store_true',help='Get scan date')
    parser.add_argument('-a','--all',action='store_true',help='Print all information')
    args = parser.parse_args()

    main(args)

