PWORK=/media/localadmin/DATA2/RADIOMICS-PROJECTS/usz_gbm-recurrence-prediction/code_data-preparation/work/9d/e514e5a9675dcd3e0fefe0c7f20392

#!/bin/bash -ue
python -m bin.feature_extractor_nii_with_preprocessing \
          --image ${PWORK}/[Aligned_T1_ax_FSPGR_3D]_____T1_37371_20160530201940.nii.gz \
          --mask ${PWORK}/seg_desc-Roi1.nii.gz \
          --config ${PWORK}/okapy_config_mr_with_std_mask.yaml \
          --modality MR_T1 \
          --label ROI-1 \
          --stdmask ${PWORK}/seg_desc-StdROI.nii.gz \
          --outdir ${PWORK}/output2/ \
          --outfile features.json \
          --loglevel debug

# standardization mean=5465.348770360907, std=278.53443796785285