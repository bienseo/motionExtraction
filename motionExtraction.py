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

def main(args):
    toNifti(args.directory)
    toAfniFormat(args.directory)
    slice_time_correction(args.directory)
    motionCorrection(args.directory)
    outputArrange(args.directory)

def toNifti(directory):
    '''
    If FALSE returns from are_there_nifti function,
    it makes 'dicom' directory under the input dir.
    Then moves all files into the 'dicom'
    (except log.txt and FREESURFER related files)
    '''
    if are_there_nifti(directory)==False:
        print '='*80,'\nDcm2nii conversion\n','='*80

        try:
            os.mkdir(os.path.join(directory,'dicom'))
        except OSError as e:
            print 'Error in making dicom directory : ',e

        files_to_move = [
            x for x in os.listdir(directory) \
                if x != 'dicom' \
                and x !='log.txt' \
                and x !='FREESURFER' \
                and x !='fsaverage' \
                and x !='lh.EC_average' \
                and x !='rh.EC_average']
        try:
            for file_to_move in files_to_move:
                shutil.move(os.path.join(directory,file_to_move),
                        os.path.join(directory,'dicom'))
        except PermissionError as e:
            print 'Error in the toNifti :',e
            pass
        else:
            print 'Jumped somthing in toNifti function : unknown'
        dcm2nii_all(directory)
    else:
        print '='*80
        print 'There are nifti files in the directory'
        print 'Jumping the directory rearrange and dicom conversion'
        print '='*80

def are_there_nifti(directory):
    '''
    Search for .nii.gz files in the user input dir
    '''
    for root, dirs, files in os.walk(directory):
        for singleFile in files:
            if re.search('nii.gz$',singleFile,flags=re.IGNORECASE):
                print singleFile
                return True
                break
    return False

def dcm2nii_all(directory):
    '''
    It uses pp to run dcm2nii jobs in parallel.
    dcm2nii jobs have inputs of the first dicom
    in each directories inside the 'dicom' directory.
    (returned using getFirstDicom function)
    '''

    job_server=pp.Server()
    jobList=[]
    dicom_source_directories = [x for x in os.listdir(os.path.join(directory,'dicom')) if x == 'REST' \
            or x == 'DTI' \
            or x == 'DKI' \
            or 'EP2D_BOLD' in x \
            or 'RUN' in x \
            or x == 'T1']

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

def getFirstDicom(directoryAddress):
    '''
    returns the name of the first dicom file
    in the directory
    '''
    for root,dirs,files in os.walk(directoryAddress):
        for singleFile in files:
            if re.search('.*ima|.*dcm',singleFile,flags=re.IGNORECASE):
                return os.path.abspath(os.path.join(directoryAddress,singleFile))

def toAfniFormat(directory):
    '''
    converts nifti images to afni format
    '''
    for root, dirs, files in os.walk(os.path.join(directory,'REST')):
        for singleFile in files:
            if re.search('nii.gz$',singleFile):
                print '.',
                command = '3dcopy {restNifti} {afniOut}'.format(
                        restNifti=os.path.join(root,singleFile),
                        afniOut=os.path.join(root,'rest'))
                output = os.popen(command).read()
    print

def slice_time_correction(directory):
    print '='*80,'\nSlice time correction\n','='*80
    command = '3dTshift \
            -verbose \
            -TR 3.5s \
            -tzero 0 \
            -prefix {restDir}/tShift_rest \
            -tpattern alt+z {restDir}/rest+orig[4..115]'.format(
                    restDir=os.path.join(directory,'REST'))
    output = os.popen(command).read()

def motionCorrection(directory):
    print '='*80,'\nMotion parameter calculation\n','='*80
    command = '3dvolreg \
            -verbose \
            -prefix {restDir}/reg \
            -dfile {restDir}/reg_param.txt \
            -maxdisp1D {restDir}/maxDisp.txt \
            {restDir}/tShift_rest+orig'.format(
                    restDir=os.path.join(directory,'REST'))
    output = os.popen(command).read()


def outputArrange(directory):
    print '='*80,'\nMake motion graph in the REST directory\n','='*80
    if '.' in directory and len(directory) < 3: #if user has given -dir ./
        subjName = re.search('[A-Z]{3}\d{2,3}',os.getcwd()).group(0)
    else:
        subjName = re.search('[A-Z]{3}\d{2,3}',directory).group(0)

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

    fig.suptitle("%s" % subjName, fontsize=20)
    fig.savefig(os.path.join(directory,'REST','%s_motion.png' % subjName))



if __name__=='__main__':
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description = textwrap.dedent('''\
            {codeName} : Returns motion parameters
            extracted from dicom within the directory
            ====================
            eg) {codeName}
            eg) {codeName} --dir /Users/kevin/NOR04_CKI
            '''.format(codeName=os.path.basename(__file__))))
    parser.add_argument(
            '-dir','--directory',
            help='Data directory location, default = pwd',
            default=os.getcwd())
    args = parser.parse_args()
    main(args)
