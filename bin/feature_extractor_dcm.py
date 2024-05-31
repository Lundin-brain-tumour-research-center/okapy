import pathlib as pl

from bin.helpers import feature_extractor_dcm
import logging

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

