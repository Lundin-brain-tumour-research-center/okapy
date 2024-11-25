import pathlib as pl
import shutil

import pandas as pd

from bin.helpers import feature_extractor_dcm, convert_dicom_to_nifti, preprocess_extract_features

p_data= pl.Path('/home/abler/repositories/NextFlow-OkaPy/assets/test-data/brain-mr')
p_mr_t1c_dcm_img = p_data.joinpath('T1c-dcm')
p_mr_t1c_dcm_seg = p_data.joinpath('dcmseg-T1c.dcm')
p_base = pl.Path(__file__).parent.parent
p_out = p_base.joinpath('output')
p_out.mkdir(exist_ok=True)
p_config = p_base.joinpath('assets/config_mr_extraction_mask_std.yaml')




# Convert DICOM to NII
p_out_convert_dcm_nii = p_out.joinpath('conversion-to-nii')
# preprcess and extract from NII
p_img_nii = p_out_convert_dcm_nii.joinpath('UPENN_UPENN-GBM-00001__MR.nii.gz')
p_img_seg_extr = p_out_convert_dcm_nii.joinpath('UPENN_UPENN-GBM-00001__Edema__SEG__MR.nii.gz')
p_img_seg_std = p_out_convert_dcm_nii.joinpath('UPENN_UPENN-GBM-00001__NET__SEG__MR.nii.gz')
p_out_extraction_from_nii = p_out.joinpath('extraction-from-nii')
p_out_extraction_from_nii.mkdir(exist_ok=True)
p_features_extraction_from_nii = p_out_extraction_from_nii.joinpath('features.json')
preprocess_extract_features(p_img_nii,
                            p_img_seg_extr,
                            p_config,
                            path_to_mask_std=p_img_seg_std,
                            modality='MR_T1c',
                            label='FLAIR',
                            p_out_dir=p_out_extraction_from_nii,
                            p_out_features=p_features_extraction_from_nii)
