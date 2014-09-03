#motion_extract.py
------------------------
2014-09-03
Kevin Cho
sky8671@gmail.com
------------------------

This code is for *CCNC MRI raw data structure*, obtained from Siemens Trio 3.0T MRI machine.

It *moves all* modality dicoms under a directory called 'dicom'. Then *only the T1, REST, DTI, DKI modalities* are converted in <nifti format> into a new directory.

* For the REST modality, the subject motion is also documented into a graph using Afni.


##usage: motionExtraction.py [-h] [-dir DIRECTORY]
eg) motionExtraction.py --dir /Users/kevin/NOR04_CKI



