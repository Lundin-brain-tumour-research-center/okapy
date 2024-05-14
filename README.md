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
         --config assets/config_mr.yaml
  ```

- Conversion of Dicom images and segmentations to NII, no preprocessing
  ```bash
  python -m bin.converter_dcm_nii \
         -i data/test_files/dicom/MR/ \
         -o output/nii/MR5/ \
         --loglevel debug \
         -l edema \
         -s output/nii/MR5/results.json
  ```


- Conversion of Dicom images and segmentations to NII, including preprocessing as for feature extraction
  ```bash
  python -m bin.converter_preprocessor_dcm_nii \
         -i data/test_files/dicom/MR/ \
         -o output/nii/MR5/ \
         --loglevel debug \
         --config assets/config_mr.yaml \
         -s output/nii/MR5/summary.csv
  ```

- Feature extraction from NII image and mask file (e.g. obtained from the conversion process above)
  ```bash
  python -m bin.feature_extractor_nii \
         -i output/nii/MR5/00005__MR_FLAIR.nii.gz \
         -m output/nii/MR5/00005___edema__SEG__MR_FLAIR.nii.gz \
         -s MR_FLAIR \
         --loglevel debug \
         --config assets/config_mr.yaml \
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
             --config /repo/assets/config_mr.yaml \
             --output_summary /repo/output/nii/MR/summary.csv \
             --loglevel debug
  ```
- Conversion of Dicom images and segmentations to NII
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base python -m bin.feature_extractor_nii \
         --image /repo/output/nii/MR/00005__MR_FLAIR.nii.gz \
         --mask /repo/output/nii/MR/00005___edema__SEG__MR_FLAIR.nii.gz \
         --modality MR_FLAIR \
         --config /repo/assets/config_mr.yaml \
         --output /repo/output/nii/features.json \
         --loglevel debug
  ```
- Feature extraction from NII image and mask file (e.g. obtained from the conversion process above)
  ```bash
  docker run --rm \
          -v "<path-to-repository>":"/repo" \
          okapy:latest \
          micromamba run -n base   python -m bin.feature_extractor_dcm \
         --input_directory /repo/data/test_files/dicom/MR/ \
         --output_filepath /repo/output/nii/features_from_dcm_all.csv \
         --config /repo/assets/config_mr.yaml \
         --loglevel debug
  ```


  python -m bin.converter_dcm_nii \
         -i data/test_files/dicom/MR/ \
         -o output/nii/MR5/ \
         --loglevel debug \
         -s output/nii/MR5/results.json
