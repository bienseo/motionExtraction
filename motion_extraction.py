#!/usr/bin/python
'''
------------------------
2014-09-03
Kevin Cho
sky8671@gmail.com
------------------------

This code is for CCNC MRI raw data structure, obtained from Siemens Trio 3.0T
MRI machine. It moves all modality dicoms under a directory called 'dicom'.
Then only the T1, REST, DTI, DKI modalities are converted in nifti format
into a new directory. For the REST modality, the subject motion is also
documented into a graph using Afni.
'''

import textwrap
import shutil
import re
import pandas as pd
import os
import argparse
import pp
import matplotlib.pyplot as plt


def main(args):
    to_nifti(args.directory,args.rest)
    to_afni_format(args.directory)
    slice_time_correction(args.directory)
    motion_correction(args.directory)

    if args.graph:
        make_graph(args.directory)

def to_nifti(directory, one_level_only):
    '''
    If FALSE returns from are_there_nifti function,
    it makes 'dicom' directory under the input dir.
    Then moves all files into the 'dicom'
    (except log.txt and FREESURFER related files)
    '''
    if are_there_nifti(directory, one_level_only) == False:
        print '='*80, '\nDcm2nii conversion\n', '='*80

        try:
            os.mkdir(os.path.join(directory, 'dicom'))
        except OSError as e:
            print 'Error in making dicom directory : ', e

        files_to_move = [
            x for x in os.listdir(directory) \
                if x != 'dicom' \
                and x != 'log.txt' \
                and x != 'FREESURFER' \
                and x != 'fsaverage' \
                and x != 'lh.EC_average' \
                and x != 'rh.EC_average']
        try:
            for file_to_move in files_to_move:
                shutil.move(os.path.join(directory, file_to_move),
                            os.path.join(directory, 'dicom'))
        except OSError as e:
            print 'Error in the to_nifti :', e
        else:
            print 'Jumped somthing in to_nifti function : unknown'
        dcm2nii_all(directory,one_level_only)
    else:
        print '='*80
        print '\tThere are nifti files in the directory'
        print '\tJumping the directory rearrange and dicom conversion'
        print '='*80


def are_there_nifti(directory, one_level_only):
    '''
    Search for .nii.gz files in the user input dir
    '''
    if one_level_only and \
       re.search('nii.gz$', ' '.join(os.listdir(directory))):
        return True
    else:
        for root, dirs, files in os.walk(directory):
            for single_file in files:
                if re.search('nii.gz$', single_file, flags=re.IGNORECASE):
                    print single_file
                    return True
                    break
    return False


def dcm2nii_all(directory,one_level_only):
    '''
    It uses pp to run dcm2nii jobs in parallel.
    dcm2nii jobs have inputs of the first dicom
    in each directories inside the 'dicom' directory.
    (returned using get_first_dicom function)
    '''

    job_server = pp.Server()
    job_list = []

    if one_level_only:
        dicom_source_directories = os.path.join(
            directory,
            'dicom')
    else:
        dicom_source_directories = [x for x in os.listdir(
            os.path.join(directory, 'dicom')) \
                if x == 'REST' \
                or x == 'DTI' \
                or x == 'DKI' \
                or 'EP2D_BOLD' in x \
                or 'RUN' in x \
                or x == 'T1']

    for dicom_source_directory in dicom_source_directories:
        nifti_out_dir = os.path.join(directory, dicom_source_directory)
        try:
            os.mkdir(nifti_out_dir)
        except:
            pass
        firstDicom = get_first_dicom(os.path.join(
            directory, 'dicom', dicom_source_directory))
        command = '/ccnc_bin/mricron/dcm2nii \
                -o {nifti_out_dir} {firstDicom}'.format(
                    nifti_out_dir=nifti_out_dir,
                    firstDicom=firstDicom)
        print '\t', re.sub('\s+', ' ', command)
        job_list.append(command)

    for job in [job_server.submit(run, (x, ), (), ("os", )) for x in job_list]:
        job()

def run(to_do):
    '''
    Belongs to the pp process
    '''
    os.popen(to_do).read()

def get_first_dicom(dir_address):
    '''
    returns the name of the first dicom file
    in the directory
    '''
    for root, dirs, files in os.walk(dir_address):
        for single_file in files:
            if re.search('.*ima|.*dcm', single_file, flags=re.IGNORECASE):
                return os.path.abspath(
                    os.path.join(dir_address, single_file))

def to_afni_format(directory):
    '''
    converts nifti images to afni format
    '''
    print '='*80, '\nNifti to afni brick\n', '='*80

    if os.path.isfile(os.path.join(directory, 'REST', 'rest+orig.BRIK')):
        print '\tAlready done'
    else:
        for root, dirs, files in os.walk(os.path.join(directory, 'REST')):
            for single_file in files:
                if re.search('nii.gz$', single_file):
                    command = '3dcopy {restNifti} {afniOut}'.format(
                        restNifti=os.path.join(root, single_file),
                        afniOut=os.path.join(root, 'rest'))
                    print '-'*80, '\n', re.sub('\s+', ' ', command)
                    print '-'*80
                    output = os.popen(command).read()

def slice_time_correction(directory):
    '''
    Uses afni 3dTshift
    '''
    print '='*80, '\nSlice time correction\n', '='*80
    command = '3dTshift \
            -verbose \
            -TR 3.5s \
            -tzero 0 \
            -prefix {restDir}/tShift_rest \
            -tpattern alt+z {restDir}/rest+orig[4..115]'.format(
                restDir=os.path.join(directory, 'REST'))
    if os.path.isfile(os.path.join(directory, 'REST', 'tShift_rest.BRIK')):
        print '\tAlready done'
    else:
        print '-'*80, '\n', re.sub('\s+', ' ', command), '\n', '-'*80
        output = os.popen(command).read()

def motion_correction(directory):
    '''
    Uses 3dvolreg
    '''
    print '='*80, '\nMotion parameter calculation\n', '='*80
    command = '3dvolreg \
            -verbose \
            -prefix {restDir}/reg \
            -dfile {restDir}/reg_param.txt \
            -maxdisp1D {restDir}/maxDisp.txt \
            {restDir}/tShift_rest+orig'.format(
                restDir=os.path.join(directory, 'REST'))
    if os.path.isfile(os.path.join(directory, 'REST', 'maxDisp.txt')):
        print '\tAlready done'
    else:
        print '-'*80, '\n', re.sub('\s+', ' ', command), '\n', '-'*80
        output = os.popen(command).read()


def make_graph(directory):
    print '='*80, '\nMake motion graph in the REST directory\n', '='*80
    if '.' in directory and len(directory) < 3: #if user has given -dir ./
        subj_name = re.search('[A-Z]{3}\d{2,3}', os.getcwd()).group(0)
    else:
        subj_name = re.search('[A-Z]{3}\d{2,3}', directory).group(0)

    df = pd.read_csv(os.path.join(
        directory, 'REST', 'reg_param.txt'),
                     sep='\s+',
                     index_col=0,
                     names=['roll', 'pitch', 'yaw', 'dS',
                            'dL', 'dP', 'rmsold', 'rmnew'])

    maxdisp_df = pd.read_csv(os.path.join(
        directory, 'REST', 'maxDisp.txt'),
                             sep='\s+',
                             skiprows=[0,1],
                             names=['maxDisp'])

    plt.ioff()
    fig = plt.figure(figsize=(12, 8))
    ax1 = plt.subplot(221)
    ax2 = plt.subplot(223)
    ax3 = plt.subplot(122)

    ax1.grid(False)
    ax2.grid(False)
    ax3.grid(False)

    df[['roll', 'pitch', 'yaw']].plot(ax=ax1,grid=False)
    ax1.set_title('Rotation')
    ax1.set_xlabel('Time points')
    ax2.set_ylabel('degree')

    df[['dS', 'dL', 'dP']].plot(ax=ax2,grid=False)
    ax2.set_title('Displacement')
    ax2.set_xlabel('Time points')
    ax2.set_ylabel('mm')

    maxdisp_df.plot(ax=ax3,grid=False)
    ax3.set_title('Maximum displacements')
    ax3.set_xlabel('Time points')
    ax3.set_ylabel('mm')
    #df.abs().describe().ix['max',
                           #['roll', 'pitch', 'yaw',
                            #'dS', 'dL', 'dP']].plot(
                                #kind='bar', ax=axes[2])

    fig.suptitle("%s" % subj_name, fontsize=20)
    fig.savefig(os.path.join(directory, 'REST', '%s_motion.png' % subj_name))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            {codeName} : Returns motion parameters
            extracted from dicom within the directory
            ====================
            eg) {codeName}
            eg) {codeName} --dir /Users/kevin/NOR04_CKI
            '''.format(codeName=os.path.basename(__file__))))
    parser.add_argument(
        '-dir', '--directory',
        help='Data directory location, default=pwd',
        default=os.getcwd())
    parser.add_argument(
        '-g', '--graph',
        help='Produce graph in png format',
        default=True)
    parser.add_argument(
        '-r', '--rest',
        help='Process the dicoms directly under the input dir',
        default=False)
    args = parser.parse_args()
    main(args)
