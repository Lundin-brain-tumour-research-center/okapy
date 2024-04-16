import pandas as pd
import yaml
import pathlib as pl
from okapy.featureextractor.featureextractor import OkapyExtractors
import numpy as np
import logging
import json

def extract_features_mask(extractor, path_to_img, path_to_mask, attribute_dict={},
                          modality='MR', p_out=None):
    result = extractor(path_to_img, path_to_mask, modality=modality)
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
        if p_out.as_posix().endswith('.csv'):
            results_df.to_csv(p_out, index=False)
        elif p_out.as_posix().endswith('.json'):
            with open(p_out, 'w') as f:
                json.dump(results_dict, f, indent=4, sort_keys=True)
    return results_df, results_dict


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Feature extraction')
    parser.add_argument("-i", "--image",
                        required=True,
                        help="image file")
    parser.add_argument("-m", "--mask",
                        required=True,
                        help="mask file")
    parser.add_argument("-s", "--modality",
                        required=True,
                        help="modality as specified in yaml config file")
    parser.add_argument("-c", "--config",
                        required=True,
                        help="yaml config file")
    parser.add_argument("-t", "--output",
                        required=False,
                        default='extraction_results.json',
                        help="feature output file [csv, json]'")
    parser.add_argument('--loglevel',
                        help='define logging level and thus verbosity of comment: debug, info, critical',
                        required=False,
                        default='info',
                        choices=['debug', 'info', 'critical'],
                        type=str)
    args = parser.parse_args()

    if args.loglevel == 'debug':
        log_level = logging.DEBUG
    elif args.loglevel == 'info':
        log_level = logging.INFO
    elif args.loglevel == 'critical':
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    logging.getLogger().setLevel(log_level)

    if args.image:
        p_img = pl.Path(args.image)
        logging.info(f" - image file : {p_img}")
    else:
        logging.fatal(f"--- image file not specified")
        raise Exception("Image file not specified")

    if args.mask:
        p_mask = pl.Path(args.mask)
        logging.info(f" - mask file : {p_mask}")
    else:
        logging.fatal(f"--- mask not specified")
        raise Exception("mask file path not specified")

    if args.modality:
        modality = args.modality
        logging.info(f" - modality : {modality}")
    else:
        logging.fatal(f"--- modality not specified")
        raise Exception("modality not specified")

    if args.config:
        p_config = pl.Path(args.config)
        logging.info(f" - config file : {p_config}")
    else:
        logging.fatal(f"--- config file not specified")
        raise Exception("config file path not specified")

    if args.output:
        p_out = pl.Path(args.output)
        logging.info(f" - output file : {p_out}")
    else:
        logging.fatal(f"--- feature output file not specified")
        raise Exception("feature output file not specified")

    params = yaml.safe_load(p_config.read_bytes())
    okapy_extractor = OkapyExtractors(params["feature_extraction"])
    results_df, results_dict = extract_features_mask(okapy_extractor, p_img, p_mask,
                                                     attribute_dict={},
                                                     modality=modality,
                                                     p_out=p_out)






#
# p_base = pl.Path(__file__).parent.parent
# p_img = p_base.joinpath("output/nii/MR5/00005__MR_FLAIR.nii.gz")
# p_mask = p_base.joinpath("output/nii/MR5/00005___edema__SEG__MR_FLAIR.nii.gz")
# p_config = p_base.joinpath("assets/config_mr.yaml")
#
# params = yaml.safe_load(p_config.read_bytes())
# okapy_extractor = OkapyExtractors(params["feature_extraction"])
# results_df, results_dict = extract_features_mask(okapy_extractor, p_img, p_mask,
#                                                         attribute_dict={},
#                                                         modality='MR')
# #
# result = self.okapy_extractors(
#                     volume_info["path"],
#                     mask_info["path"],
#                     modality=volume_info["modality"])
#                 for key, val in result.items():
#                     if "diagnostics" in key:
#                         continue
#
#                     result_dict = {
#                         "patient_id": study.patient_id,
#                         "modality": volume_info["modality"],
#                         "VOI": mask_info["label"],
#                         "feature_name": key,
#                         "feature_value": val,
#                     }
#                     result_dict.update({
#                         k: getattr(volume.dicom_header, k)
#                         for k in self.additional_dicom_tags
#                     })
#                     results_df = pd.concat([
#                         results_df,
#                         pd.DataFrame(result_dict, index=[index]),
#                     ])
