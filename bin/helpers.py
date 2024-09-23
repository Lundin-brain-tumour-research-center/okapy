import json
import pathlib as pl
import SimpleITK as sitk
import numpy as np
import pandas as pd

import okapy.dicomconverter.volume_processor
from okapy.dicomconverter.converter import ExtractorConverter, NiftiConverter
from okapy.dicomconverter.dicom_walker import DicomWalker
from okapy.dicomconverter.volume import Volume, BinaryVolume, ReferenceFrame
from okapy.dicomconverter.dicom_header import DicomHeader
from okapy.dicomconverter.study import bb_union, bb_intersection
from okapy.dicomconverter.volume_processor import VolumeProcessorStack
from okapy.featureextractor.featureextractor import OkapyExtractors

from itertools import product
import yaml
import logging

from okapy.utils import NpEncoder


def project_bb(bb_vx, reference_frame, new_reference_frame):
    """
    Function from okapy.dicomconverter.study.StudyProcessor
    """
    points = [
        np.array([pr, pc, ps, 1])
        for pr, pc, ps in product(*zip(bb_vx[:3], bb_vx[3:]))
    ]
    projection_matrix = np.dot(new_reference_frame.inv_coordinate_matrix,
                               reference_frame.coordinate_matrix)
    projected_points = np.stack(
        [np.dot(projection_matrix, p)[:3] for p in points], axis=-1)
    bb_proj = np.zeros((6,))
    bb_proj[:3] = np.min(projected_points, axis=-1)
    bb_proj[3:] = np.max(projected_points, axis=-1)
    return bb_proj


def get_new_reference_frame(volume, masks_list, padding):
    """
    Function from okapy.dicomconverter.study.StudyProcessor
    """
    if masks_list is not None:
        bb_vx = bb_union([
            project_bb(mask.bb_vx, mask.reference_frame,
                             volume.reference_frame) for mask in masks_list
        ])

        bb_vx[:3] = (
                bb_vx[:3] -
                np.round(padding / volume.reference_frame.voxel_spacing))
        bb_vx[3:] = (
                bb_vx[3:] +
                np.round(padding / volume.reference_frame.voxel_spacing))

        bb_volume = np.concatenate([[0, 0, 0], volume.reference_frame.shape])
        bb_vx = bb_intersection([bb_volume, bb_vx])

        return ReferenceFrame(
            origin=volume.reference_frame.vx_to_mm(bb_vx[:3]),
            orientation_matrix=volume.reference_frame.orientation_matrix,
            voxel_spacing=volume.reference_frame.voxel_spacing,
            last_point_coordinate=volume.reference_frame.vx_to_mm(bb_vx[3:]),
        )
    else:
        logging.warning("No masks provided -> will use volume reference frame")
        return volume.reference_frame

def get_reference_frame_from_sitk(img_sitk):
    orientation_matrix = np.array(img_sitk.GetDirection()).reshape(3, 3)

    matrix = np.zeros((4, 4))
    matrix[:3, :3] = orientation_matrix * img_sitk.GetSpacing()
    matrix[:3, 3] = img_sitk.GetOrigin()
    matrix[3, 3]  = 1

    ref_frame = ReferenceFrame.from_coordinate_matrix(matrix,shape=img_sitk.GetSize())
    return ref_frame

def get_volume_from_sitk(img_sitk, modality, dicom_header=None):
    if not dicom_header:
        dicom_header = DicomHeader(patient_id=1,
                                   patient_name='test',
                                   series_date='20000101',
                                   series_time='101010',
                                   modality=modality)

    img_np = sitk.GetArrayFromImage(img_sitk)
    img_np_transp = np.transpose(img_np, (2, 1, 0))
    ref_frame = get_reference_frame_from_sitk(img_sitk)

    img_vol = Volume(array=img_np_transp,
                     reference_frame=ref_frame,
                     modality=modality,
                     dicom_header=dicom_header)

    return img_vol

def get_binary_volume_from_sitk(img_sitk, ref_volume, label=None, dicom_header=None):
    if not dicom_header:
        dicom_header = DicomHeader(patient_id=1,
                                   patient_name='test',
                                   series_date='20000101',
                                   series_time='101010')

    img_np = sitk.GetArrayFromImage(img_sitk)
    img_np_transp = np.transpose(img_np, (2, 1, 0))
    ref_frame = get_reference_frame_from_sitk(img_sitk)

    img_vol = BinaryVolume(array=img_np_transp,
                     reference_frame=ref_frame,
                     dicom_header=dicom_header,
                     label=label,
                     reference_dicom_header=ref_volume.dicom_header,
                     reference_modality=ref_volume.modality)

    return img_vol

def image_mask_preprocessor(path_to_img: pl.Path,
                             path_to_mask_extr: pl.Path,
                             path_to_config: pl.Path,
                             modality: str,
                             label: str,
                             path_to_mask_std=None,
                             p_out=None,
                             padding=10):
    """
    Given an image and mask file, this function performs image and mask preprocessing based on OKAPY configuration file,
    and using standard OKAPY functions.
    The output image and mask files are cropped to the BB of the mask plus a padding.

    Supported:
        - bspline_resampler, binary_bspline_resampler
        - standardizer
        - masked_standardizer_from_file
          -> substitutes masked_standardizer for nii-based extractions!
          path_to_mask_std defines mask to be used for standardization across all modalities!
    Not supported:
        - masked_standardizer
        - combined_standardizer
    """
    img_sitk = sitk.ReadImage(path_to_img.as_posix())
    seg_sitk = sitk.ReadImage(path_to_mask_extr.as_posix())

    with open(path_to_config, 'r') as f:
            params = yaml.safe_load(f)

    img_vol  = get_volume_from_sitk(img_sitk, modality=modality)
    mask_vol = get_binary_volume_from_sitk(seg_sitk, img_vol, label=label)

    mask_processor = VolumeProcessorStack.from_params(params["mask_preprocessing"])
    volume_processor = VolumeProcessorStack.from_params(params["volume_preprocessing"],
                                                        mask_resampler=mask_processor)
    masks_list = [mask_vol]

    if path_to_mask_std is not None:
        path_to_mask_std = pl.Path(path_to_mask_std)
        seg_std_sitk = sitk.ReadImage(path_to_mask_std.as_posix())
        mask_std = get_binary_volume_from_sitk(seg_std_sitk, img_vol, label=label)
        masks_list.append(mask_std) # ensure that processed volume not only contains extraction mask, but also standardization mask
        for stack_name, stack in volume_processor.stacks.items():
            for processor in stack:
                if isinstance(processor, okapy.dicomconverter.volume_processor.MaskedStandardizerFromFile):
                    print(f"Processor {processor} is MaskedStandardizerFromFile -> adding binary volume")
                    processor.mask_array = mask_std

    new_ref_frame = get_new_reference_frame(img_vol, masks_list, padding=padding)

    if not p_out:
        p_out = pl.Path('.')
    else:
        p_out = pl.Path(p_out)
    p_img_out = p_out.joinpath('image_processed.nii.gz')
    p_mask_out = p_out.joinpath('mask_processed.nii.gz')
    p_out.mkdir(exist_ok=True, parents=True)

    volume_processed = volume_processor(img_vol, new_reference_frame=new_ref_frame)
    sitk.WriteImage(volume_processed.sitk_image, p_img_out.as_posix())

    mask_processed = mask_processor(mask_vol, new_reference_frame=volume_processed.reference_frame)
    sitk.WriteImage(mask_processed.sitk_image, p_mask_out.as_posix())

    logging.info(f"Processing image written to {p_img_out.as_posix()}")
    logging.info(f"Processing mask written to {p_mask_out.as_posix()}")
    return p_img_out, p_mask_out


def extract_features_mask(path_to_img, path_to_mask, path_config,
                          attribute_dict={},
                          modality='MR', p_out=None):
    params = yaml.safe_load(path_config.read_bytes())
    okapy_extractor = OkapyExtractors(params["feature_extraction"])
    result = okapy_extractor(path_to_img, path_to_mask, modality=modality)
    series_list = []
    diagnostics_dict = {}
    feature_dict = {}
    for key, val in result.items():
        if isinstance(val, np.ndarray):
            val = float(val)
        # assemble json
        if key.startswith('diagnostics'):
            diagnostics_dict[key] = val
        else:
            feature_dict[key] = val
        # assemble dataframe
        attribute_dict_int = {"name": key,
                              "value": val}
        attribute_dict_int.update(attribute_dict)
        series_list.append(pd.Series(attribute_dict_int))
    results_df = pd.concat(series_list, axis=1).T
    results_dict = {'diagnostics' : diagnostics_dict,
                    'features' : feature_dict}
    results_df['type'] = results_df.name.apply(lambda x: 'diagnostics' if x.startswith('diagnostics') else 'feature')
    if p_out is not None:
        p_out = pl.Path(p_out)
        p_out.parent.mkdir(parents=True, exist_ok=True)
        if p_out.as_posix().endswith('.csv'):
            results_df.to_csv(p_out, index=False)
        elif p_out.as_posix().endswith('.json'):
            with open(p_out, 'w') as f:
                json.dump(results_dict, f, cls=NpEncoder, indent=4, sort_keys=True)

    return results_df, results_dict

def preprocess_extract_features(path_to_img: pl.Path,
                                 path_to_mask_extr: pl.Path,
                                 path_to_config: pl.Path,
                                 modality: str,
                                 label: str,
                                 path_to_mask_std=None,
                                 p_out_dir=None,
                                 p_out_features=None,
                                 padding=10):
    p_img_proc, p_mask_proc = image_mask_preprocessor(path_to_img, path_to_mask_extr, path_to_config,
                                                       path_to_mask_std=path_to_mask_std,
                                                      modality=modality, label=label, p_out=p_out_dir, padding=padding)
    results_df, results_dict = extract_features_mask(p_img_proc, p_mask_proc, path_to_config,
                                                     attribute_dict={},
                                                     modality=modality, p_out=p_out_features)
    return results_df, results_dict

def feature_extractor_dcm(
    input_directory: pl.Path,
    output_filepath: pl.Path,
    p_config: pl.Path
):
    """
    Extracts features from all ROIs found in RT-STRUCT/DCM-SEG DCM-series pairs in input_directory.
    Extraction (including DCM image series preprocess) settings are provided via YAML configuration file.
    Feature values are saved to output_filepath (csv file).
    """
    if p_config.exists():
        converter = ExtractorConverter.from_params(p_config)
        results = converter(input_directory)
        results.to_csv(output_filepath, index=False)
        logging.info(f"Extraction results were saved to {output_filepath}")
        return results

    else:
        logging.fatal(f"Parameter file {p_config} does not exist")


def convert_dicom_to_nifti(
    input_directory: pl.Path,
    output_filepath: pl.Path,
    p_results_info=None,
    labels_startswith=None
):
    """
    Convert to dicom to the right format based on extension
    """
    if not output_filepath.exists():
        logging.info(f" - Creating folder {output_filepath}")
        output_filepath.mkdir(parents=True, exist_ok=True)

    converter = NiftiConverter(
        padding="whole_image",
        labels_startswith=labels_startswith,
        dicom_walker=DicomWalker(),
    )
    result = converter(input_directory, output_folder=output_filepath)

    if p_results_info is None:
        p_results_info = output_filepath.joinpath("results.json")
    p_results_info.parent.mkdir(exist_ok=True, parents=True)

    with open(p_results_info, "w") as outfile:
        json.dump(result, outfile, cls=NpEncoder, indent=4, sort_keys=True)

    logging.info(f"Converted images/masks written to '{output_filepath}', summary of converted files to '{p_results_info}'.")

    return result
