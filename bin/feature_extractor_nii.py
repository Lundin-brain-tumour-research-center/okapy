import yaml
import pathlib as pl
from bin.helpers import extract_features_mask
import logging

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
    parser.add_argument("-f", "--outfile",
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

    if args.outfile:
        p_out = pl.Path(args.outfile)
        logging.info(f" - output file : {p_out}")
    else:
        logging.fatal(f"--- feature output file not specified")
        raise Exception("feature output file not specified")

    results_df, results_dict = extract_features_mask(p_img, p_mask, p_config,
                                                     attribute_dict={},
                                                     modality=modality,
                                                     p_out=p_out)





