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
p_config = p_base.joinpath('assets/config_mr_extraction.yaml')


# Extract features from DICOM
p_dcm_img_seg = p_out.joinpath('dcm-img-seg')
p_dcm_img_seg.mkdir(exist_ok=True)
for file in p_mr_t1c_dcm_img.glob('*.dcm'):
    shutil.copy(file, p_dcm_img_seg.joinpath(file.name))
shutil.copy(p_mr_t1c_dcm_seg, p_dcm_img_seg.joinpath(p_mr_t1c_dcm_seg.name))

p_out_extraction_from_dcm = p_out.joinpath('extraction-from-dcm').joinpath('features.csv')
p_out_extraction_from_dcm.parent.mkdir(exist_ok=True)
result = feature_extractor_dcm(p_dcm_img_seg, p_out_extraction_from_dcm, p_config=p_config)

# Convert DICOM to NII
p_out_convert_dcm_nii = p_out.joinpath('conversion-to-nii')
p_out_convert_dcm_nii.mkdir(exist_ok=True)
convert_dicom_to_nifti(p_dcm_img_seg, p_out_convert_dcm_nii, p_results_info=p_out_convert_dcm_nii.joinpath('info.json'))

# preprcess and extract from NII
p_img_nii = p_out_convert_dcm_nii.joinpath('UPENN_UPENN-GBM-00001__MR.nii.gz')
p_img_seg = p_out_convert_dcm_nii.joinpath('UPENN_UPENN-GBM-00001__Edema__SEG__MR.nii.gz')
p_out_extraction_from_nii = p_out.joinpath('extraction-from-nii')
p_out_extraction_from_nii.mkdir(exist_ok=True)
p_features_extraction_from_nii = p_out_extraction_from_nii.joinpath('features.json')
preprocess_extract_features(p_img_nii, p_img_seg, p_config,
                            modality='MR_T1c',
                            label='FLAIR',
                            p_out_dir=p_out_extraction_from_nii,
                            p_out_features=p_features_extraction_from_nii)

#== compare features
# (1) from NII
import json
with open(p_features_extraction_from_nii) as json_file:
    features_from_nii = json.load(json_file)['features']
features_from_nii = pd.Series(features_from_nii, name='from_nii')
# (2) from dcm
import pandas as pd
df_features_from_dcm = pd.read_csv(p_out_extraction_from_dcm)
sel_cond = (df_features_from_dcm['modality']=='MR_T1c') & (df_features_from_dcm['VOI']=='Edema')
df_features_from_dcm_sel = df_features_from_dcm[sel_cond]
features_from_dcm = df_features_from_dcm_sel.set_index('feature_name')['feature_value']
features_from_dcm.name = 'from_dcm'

# (2) from dcm QI
df_features_from_dcm_QI = pd.read_csv(p_out.joinpath('extraction-from-dcm-QI').joinpath('features_album_okapy-extraction-comparison_MR_T1c-Edema.csv'))
cols_new = [col.replace('_intensity_', '_firstorder_') for col in df_features_from_dcm_QI.columns]
df_features_from_dcm_QI.columns =cols_new
features_from_dcm_QI = df_features_from_dcm_QI.drop(['PatientID', 'Modality', 'ROI'], axis=1).T.squeeze()
features_from_dcm_QI.name = 'from_dcm_qi'

df = pd.concat([features_from_nii, features_from_dcm_QI, features_from_dcm], axis=1)

df['rel_diff_from_nii'] = (df['from_nii'] - df['from_dcm_qi']) / df['from_dcm_qi']
df['rel_diff_from_dcm'] = (df['from_dcm'] - df['from_dcm_qi']) / df['from_dcm_qi']