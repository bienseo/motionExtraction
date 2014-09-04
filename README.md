motion_extract.py
---------------------

2014-09-03


This code is for *CCNC MRI raw data structure*, obtained from Siemens Trio 3.0T MRI machine.

It *moves all* modality dicoms under a directory called 'dicom'. Then *only the T1, REST, DTI, DKI modalities* are converted to **nifti format** into new directories.

* For the REST modality, the subject motion is also documented into a graph using Afni.

###External dependencies

matplotlib
    \-pyplot (motion_extraction)
pandas (motion_extraction)
pp (motion_extraction)


###usage: 
```
motionExtraction.py [-h] [-dir DIRECTORY]

eg) motionExtraction.py --dir /Users/kevin/NOR04_CKI
```



