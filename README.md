## Okapy Documentation
[Okapy Documentation](https://voreille.github.io/okapy/)

## Examples for Commandline Usage
Configuration of all processes below relies on the OkaPy parameters file for
- volume / image pre-processing and conversion
- mask pre-processing and conversion
- feature extraction

### Commandline Scripts:
- Feature extraction from images and segmentations in DCM directory:
  ```bash
  python -m bin.feature_extractor_dcm \
         -i data/test_files/dicom/MR/ \
         -o output/features.csv \
         --loglevel debug \
         --config assets/config_mr_extraction.yaml
  ```
  This script performs the preprocessing and feature extraction steps defined in the `--config` file,
  completely analogous to the preprocessing and feature extraction performed by QuantImage.

- Conversion of Dicom images and segmentations to NII, no preprocessing:
  ```bash
  python -m bin.converter_dcm_nii \
         -i data/test_files/dicom/PTCT/CHUS005/ \
         -o output/nii/PETCT/CHUS005/ \
         -l GTV \
         -s output/nii/PETCT/CHUS005/results.json \
         --loglevel debug 
  ```
  This script will convert all dicom series found in the input directory to nii files.
  Files will be named by their modality (CT, PT, MR).
  When multiple files of the same modality are present (e.g. different types of MR),
  the resulting nii files will be stored under the same name.
  Intensity values in CT and PT images will be converted to HU and SUV, respectively.
  The `-l` input option allows selecting the ROIs of associated segmentation files that are to
  be converted into nii masks. In the absence of `-l` input, all ROIs will be converted.

- Preprocessing of NII image and mask file:
  ```bash
  python -m bin.image_mask_preprocessor_nii \
         -i output/nii/PETCT/CHUS005/HN-CHUS-005__PT.nii.gz \
         -m output/nii/PETCT/CHUS005/HN-CHUS-005__GTV__RTSTRUCT__CT.nii.gz \
         -c assets/config_petct_extraction.yaml \
         -s PT \
         -l GTV \
         -d output/preprocessing-PETCT/ \
         --loglevel debug 
  ```
  This script performs the preprocessing steps defined in the `--config` file,
  completely analogous to the preprocessing performed by QuantImage.

- Feature extraction from NII image and mask file (e.g. obtained from the conversion and or preprocessing processes above)
  ```bash
  python -m bin.feature_extractor_nii \
         -i output/preprocessing-PETCT/image_processed.nii.gz \
         -m output/preprocessing-PETCT/mask_processed.nii.gz \
         -s PT \
         --loglevel debug \
         --config assets/config_petct_extraction.yaml \
         -f output/features-PETCT/features.json
  ```


- Image / mask preprocessing and feature extraction from NII:
  (combines functions `image_mask_preprocessor_nii` and `feature_extractor_nii`)  
  ```bash
  python -m bin.feature_extractor_nii_with_preprocessing \
         -i output/nii/PETCT/CHUS005/HN-CHUS-005__PT.nii.gz \
         -m output/nii/PETCT/CHUS005/HN-CHUS-005__GTV__RTSTRUCT__CT.nii.gz \
         -c assets/config_petct_extraction.yaml \
         -s PT \
         -l GTV \
         -d output/preprocessing-extraction-PETCT/ \
         -f output/preprocessing-extraction-PETCT/features.json \
         --loglevel debug 
  ```
  

### Usage via Docker

Build a docker container for the OkaPy library via
```bash
docker build . -t okapy
```

- Feature extraction from images and segmentations in DCM directory:
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base python -m bin.converter_preprocessor_dcm_nii \
             --input_directory /repo/data/test_files/dicom/MR/ \
             --output_directory /repo/output/nii/MR/ \
             --config /repo/assets/config_mr_extraction.yaml \
             --output_summary /repo/output/nii/MR/summary.csv \
             --loglevel debug
  ```

- Conversion of Dicom images and segmentations to NII
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base python -m bin.converter_dcm_nii \
            -i /repo/data/test_files/dicom/PTCT/CHUS005/ \
            -o /repo/output/nii/PETCT/CHUS005/ \
            -l GTV \
            -s /repo/output/nii/PETCT/CHUS005/results.json \
            --loglevel debug 
  ```

- Preprocessing of NII image and mask file:
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base python -m bin.image_mask_preprocessor_nii \
            -i /repo/output/nii/PETCT/CHUS005/HN-CHUS-005__PT.nii.gz \
            -m /repo/output/nii/PETCT/CHUS005/HN-CHUS-005__GTV__RTSTRUCT__CT.nii.gz \
            -c /repo/assets/config_petct_extraction.yaml \
            -s PT \
            -l GTV \
            -d /repo/output/preprocessing-PETCT/ \
            --loglevel debug 
  ```
  
- Feature extraction from NII image and mask file (e.g. obtained from the conversion process above)
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base   python -m bin.feature_extractor_nii \
            -i /repo/output/preprocessing-PETCT/image_processed.nii.gz \
            -m /repo/output/preprocessing-PETCT/mask_processed.nii.gz \
            -s PT \
            --loglevel debug \
            --config /repo/assets/config_petct_extraction.yaml \
            -f /repo/output/features-PETCT/features.json
  ```

- Image / mask preprocessing and feature extraction from NII:
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base   python -m bin.feature_extractor_nii_with_preprocessing \         
            -i /repo/output/nii/PETCT/CHUS005/HN-CHUS-005__PT.nii.gz \
            -m /repo/output/nii/PETCT/CHUS005/HN-CHUS-005__GTV__RTSTRUCT__CT.nii.gz \
            -c /repo/assets/config_petct_extraction.yaml \
            -s PT \
            -l GTV \
            -d /repo/output/preprocessing-extraction-PETCT/ \
            -f /repo/output/preprocessing-extraction-PETCT/features.json \
            --loglevel debug 
  ```
