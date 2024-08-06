import pathlib as pl

from bin.helpers import convert_dicom_to_nifti
import logging

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
    parser.add_argument("-l", "--labels",
                        help="Starting string indicating the subset of labels to extract along with the dcm images",
                        required=False,
                        default=None, # all labels are extracted
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

    result = convert_dicom_to_nifti(p_in, p_out,
                                    p_results_info=p_summary,
                                    labels_startswith=args.labels)

