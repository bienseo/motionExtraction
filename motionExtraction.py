#!/Users/admin/anaconda/bin/python

import textwrap
import shutil
import re
import pandas as pd
import os
import argparse
import pp
import matplotlib.pyplot as plt

pd.options.display.mpl_style = 'default'

# In[83]:
def are_there_nifti(directory):
    check_for_nifti = False
    for root, dirs, files in os.walk(directory):
        for singleFile in files:
            if re.search('nii.gz$',singleFile,flags=re.IGNORECASE):
                print singleFile
                return True
                break
    return check_for_nifti


def getFirstDicom(directoryAddress):
    for root,dirs,files in os.walk(directoryAddress):
        for singleFile in files:
            if re.search('.*ima|.*dcm',singleFile,flags=re.IGNORECASE):
                return os.path.abspath(os.path.join(directoryAddress,singleFile))

def dcm2nii_all(directory):
    job_server=pp.Server()
    jobList=[]
    dicom_source_directories = [x for x in os.listdir(os.path.join(directory,'dicom')) if x != 'log.txt']
    for dicom_source_directory in dicom_source_directories:
        niftiOutDir = os.path.join(directory,dicom_source_directory)
        try:
            os.mkdir(niftiOutDir)
        except:
            pass
        firstDicom = getFirstDicom(os.path.join(directory,'dicom',dicom_source_directory))
        command = '/ccnc_bin/mricron/dcm2nii \
                -o {niftiOutDir} {firstDicom}'.format(niftiOutDir=niftiOutDir,
                        firstDicom=firstDicom)
        jobList.append(command)

    for job in [job_server.submit(run,(x,),(),("os",)) for x in jobList]:
        job()


def run(toDo):
    os.popen(toDo).read()

def main(args):
    check_for_nifti = are_there_nifti(args.directory) #TRUE if there are nifti

    #if there is no nifti
    if check_for_nifti==False:
        print 'dcm2nii conversion'
        #move all directories under 'dicom'
        try:
            os.mkdir(os.path.join(args.directory,'dicom'))
            modalityDirectories = [x for x in os.listdir(args.directory) if x != 'dicom' or x != 'log.txt']
            for directory in modalityDirectories:
                shutil.move(os.path.join(args.directory,directory),
                        os.path.join(args.directory,'dicom'))
        except:
            pass

        dcm2nii_all(args.directory)

    toAfniFormat(args.directory)
    slice_time_correction(args.directory)
    motionCorrection(args.directory)
    outputArrange(args.directory)

def toAfniFormat(directory):
    for root, dirs, files in os.walk(os.path.join(directory,'REST')):
        for singleFile in files:
            if re.search('nii.gz$',singleFile):
                command = '3dcopy {restNifti} {afniOut}'.format(
                        restNifti=os.path.join(root,singleFile),
                        afniOut=os.path.join(root,'rest'))
                os.popen(command).read()

def slice_time_correction(directory):
    command = '3dTshift \
            -verbose \
            -TR 3.5s \
            -tzero 0 \
            -prefix {restDir}/tShift_rest \
            -tpattern alt+z {restDir}/rest+orig[4..115]'.format(
                    restDir=os.path.join(directory,'REST'))
    os.popen(command).read()

def motionCorrection(directory):
    command = '3dvolreg \
            -verbose \
            -prefix {restDir}/reg \
            -dfile {restDir}/reg_param.txt \
            -maxdisp1D {restDir}/maxDisp.txt \
            {restDir}/tShift_rest+orig'.format(
                    restDir=os.path.join(directory,'REST'))
    os.popen(command).read()


def outputArrange(directory):
    df = pd.read_csv(os.path.join(directory,
        'REST','reg_param.txt'),
        sep='\s+',
        index_col=0,
        names=['roll','pitch','yaw','dS','dL','dP','rmsold','rmnew'])

    plt.ioff()
    fig,axes = plt.subplots(nrows=3,figsize=(15,10))
    df[['roll','pitch','yaw']].plot(ax=axes[0])
    axes[0].set_title('Rotation')
    df[['dS','dL','dP']].plot(ax=axes[1])
    axes[1].set_title('Displacement')
    axes[1].set_ylabel('mm')
    df.abs().describe().ix['max',['roll','pitch','yaw','dS','dL','dP']].plot(kind='bar',ax=axes[2])
    axes[2].set_title('Max measurements')

    fig.savefig(os.path.join(directory,'REST','motion.png'))



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
    args = parser.parse_args()
    main(args)
