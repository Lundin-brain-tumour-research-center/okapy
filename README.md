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
         -i data/test_files/dicom/MR/ \
         -o output/nii/MR5/ \
         --loglevel debug \
         -l edema \
         -s output/nii/MR5/results.json
  ```
  This script will convert all dicom series found in the input directory to nii files.
  Files will be named by their modality (CT, PT, MR).
  When multiple files of the same modality are present (e.g. different types of MR),
  the resulting nii files will be stored under the same name.
  Intensity values in CT and PT images will be converted to HU and SUV, respectively.
  The `-l` input option allows selecting the ROIs of associated segmentation files that are to
  be converted into nii masks. In the absence of `-l` input, all ROIs will be converted.


- Feature extraction from NII image and mask file (e.g. obtained from the conversion process above)
  ```bash
  python -m bin.feature_extractor_nii \
         -i output/nii/MR5/00005__MR_FLAIR.nii.gz \
         -m output/nii/MR5/00005___edema__SEG__MR_FLAIR.nii.gz \
         -s MR_FLAIR \
         --loglevel debug \
         --config assets/config_mr_extraction.yaml \
         -t output/nii/features.json
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
         -i /repo/data/test_files/dicom/MR/ \
         -o /repo/output/nii/MR5/ \
         --loglevel debug \
         -l edema \
         -s /repo/output/nii/MR5/results.json
  ```

- Feature extraction from NII image and mask file (e.g. obtained from the conversion process above)
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base   python -m bin.feature_extractor_dcm \
         --input_directory /repo/data/test_files/dicom/MR/ \
         --output_filepath /repo/output/nii/features_from_dcm_all.csv \
         --config /repo/assets/config_mr_extraction.yaml \
         --loglevel debug
  ```

