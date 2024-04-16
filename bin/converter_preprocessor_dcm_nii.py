import pathlib as pl
from okapy.dicomconverter.converter import NiftiConverter, ExtractorConverter
import logging

def convert_dicom_to_nifti(
    input_directory: pl.Path,
    output_filepath: pl.Path,
    p_config=None,
    p_results_info=None
):
    """
    Convert to dicom to the right format based on extension
    """
    if not output_filepath.exists():
        logging.info(f" - Creating folder {output_filepath}")
        output_filepath.mkdir(parents=True, exist_ok=True)

    converter = NiftiConverter.from_params(p_config)
    result = converter(input_directory, output_folder=output_filepath)
    if p_results_info is None:
        p_results_info = output_filepath.joinpath("results.csv")
    p_results_info.parent.mkdir(exist_ok=True, parents=True)
    result.to_csv(p_results_info)
    logging.info(f"Converted images/masks written to '{output_filepath}', summary of converted files to '{p_results_info}'.")
    return result
#
# p_base = pl.Path(__file__).parent.parent
# p_in = p_base.joinpath("data/test_files/dicom/MR/")
# p_out = p_base.joinpath("output/nii/MR4/")
# p_config = p_base.joinpath("assets/config_mr.yaml")
# result = convert_dicom_to_nifti(p_in, p_out,
#                            naming=0,
#                                 list_labels=['edema'],
#                            p_config=p_config)
#

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='DICOM converter')
    parser.add_argument("-i", "--input_directory",
                        help="Directory with dicom files",
                        required=True,
                        type=str)
    parser.add_argument("-o", "--output_directory",
                        help="Path to nii output directory",
                        required=False,
                        default='output',
                        type=str)
    parser.add_argument("-s", "--output_summary",
                        help="Path to csv summary",
                        required=False,
                        default='results.csv',
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

    p_out = pl.Path(args.output_directory)
    logging.info(f" - output directory : {p_out}")

    p_summary = pl.Path(args.output_summary)
    logging.info(f" - output summary : {p_summary}")

    if args.config:
        p_config = pl.Path(args.config)
        if p_config.exists():
            logging.info(f" - config file : {p_config}")
        else:
            logging.fatal(f" - config file '{p_config}' not found ... proceeding without config")
            p_config = None
    else:
        p_config = None


    result = convert_dicom_to_nifti(p_in, p_out,
                           p_results_info=p_summary,
                           p_config=p_config)

