import pathlib as pl
import logging
from bin.helpers import preprocess_extract_features


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Feature extractor with image & mask preprocessor')
    parser.add_argument("-i", "--image",
                        required=True,
                        help="image file")
    parser.add_argument("-m", "--mask",
                        required=True,
                        help="mask file")
    parser.add_argument("-t", "--stdmask",
                        required=False,
                        help="mask file for standardization",
                        default=None)
    parser.add_argument("-c", "--config",
                        required=True,
                        help="yaml config file")
    parser.add_argument("-s", "--modality",
                        required=True,
                        help="modality as specified in yaml config file")
    parser.add_argument("-d", "--outdir",
                        required=False,
                        default='.',
                        help="output directory")
    parser.add_argument("-f", "--outfile",
                        required=False,
                        default='extraction_results.json',
                        help="feature output file [csv, json]'")
    parser.add_argument("-l", "--label",
                        required=False,
                        default='ROI',
                        help="ROI label")
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

    preprocess_extract_features(p_img, p_mask, p_config,
                            modality=modality,
                            label=args.label,
                            p_out_dir=args.outdir,
                            p_out_features=args.outfile,
                            path_to_mask_std=args.stdmask)