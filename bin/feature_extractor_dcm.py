import pathlib as pl
from okapy.dicomconverter.converter import NiftiConverter, ExtractorConverter
import logging
import pandas as pd

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

#
# p_base = pl.Path(__file__).parent.parent
# p_in = p_base.joinpath("data/test_files/dicom/MR/")
# p_out = p_base.joinpath("output/nii/features_from_dicom.csv")
# p_config = p_base.joinpath("assets/config_mr.yaml")
# result = feature_extractor_dcm(p_in,p_out,p_config)



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Feature Extractor')
    parser.add_argument("-i", "--input_directory",
                        help="Directory with dicom files",
                        required=True,
                        type=str)
    parser.add_argument("-o", "--output_filepath",
                        help="Path csv feature output",
                        required=False,
                        default='features.csv',
                        type=str)
    parser.add_argument("-c", "--config",
                        help="Path to yaml configuration file",
                        required=True,
                        type=str)
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

    if args.input_directory:
        p_in = pl.Path(args.input_directory)
        logging.info(f" - input directory : {p_in}")
    else:
        logging.fatal(f"--- input directory not specified")
        raise Exception("Input directory not specified")

    p_out = pl.Path(args.output_filepath)
    logging.info(f" - output file : {p_out}")

    if args.config:
        p_config = pl.Path(args.config)
        if p_config.exists():
            logging.info(f"- config file : {p_config}")
        else:
            logging.fatal(f"- config file '{p_config}' not found ... proceeding without config")
            p_config = None
    else:
        p_config = None

    result = feature_extractor_dcm(p_in, p_out,
                               p_config=p_config)
    print(result)

