#!/Users/admin/anaconda/bin/python

import textwrap
import dicom
import shutil
import re
import os
import sys
import argparse
import pp


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

def are_there_nifti(firstDicomFile,directory):
    check_for_nifti = False
    for root, dirs, files in os.walk(directory):
        if re.search('REST$',root):
            for singleFile in files:
                if re.search('nii.gz$',singleFile,flags=re.IGNORECASE):
                    check_for_nifti = True

    return check_for_nifti

def getFirstDicom(directoryAddress):
    for root,dirs,files in os.walk(directoryAddress):
        for singleFile in files:
            if re.search('.*ima|.*dcm',singleFile,flags=re.IGNORECASE):
                return singleFile

def dcm2nii_all(directory):
    job_server=pp.Server()
    jobList=[]
    dicom_source_directories = os.listdir(os.path.join(directory,'dicom'))
    for dicom_source_directory in dicom_source_directories:
        niftiOutDir = os.path.join(directory,dicom_source_directory)
        os.mkdir(niftiOutDir)
        firstDicom = getFirstDicom(dicom_source_directory)
        command = '/ccnc_bin/mricron/dcm2nii \
                -o {niftiOutDir} {firstDicom}'.format(niftiOutDir=niftiOutDir,
                        firstDicom=firstDicom)
        job_server.submit(command)

def main(args):
    firstDicomFile=getDicomInfo(args.foldername)#get first dicom file of the REST directory
    check_for_nifti = are_there_nifti(firstDicomFile,args.foldername) #TRUE if there are nifti

    #if there is no nifti
    if not check_for_nifti:
        #move all directories under 'dicom'
        os.mkdir(os.path.join(args.foldername,'dicom'))
        modalityDirectories = [x for x in os.listdir(args.foldername) if x != 'dicom']
        for directory in modalityDirectories:
            shutil.move(os.path.join(args,foldername,directory),
                    os.path.join(args.foldername,'dicom',directory))

    dcm2nii_all(args.foldername)


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

