# ESP Packaged Programmer Action

This repository provides a reusable action for turning your esp-idf binaries
into executables which program the esp chip. It may work for other platforms on
espressif chips such as Arduino / Platform.IO, but I have not designed / tested
it with those environments.

For an example repository which uses this action, please see
[esp-usb-ble-hid](https://github.com/finger563/esp-usb-ble-hid).

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [ESP Packaged Programmer Action](#esp-packaged-programmer-action)
  - [About](#about)
    - [Required Build Artifacts](#required-build-artifacts)
    - [Optional Build Artifacts](#optional-build-artifacts)
  - [Using this action](#using-this-action)
    - [Inputs](#inputs)

<!-- markdown-toc end -->

## About

The output of this action is a binary which requires no other dependencies,
files, or installation, but allows anyone to flash your code onto the
appropriate espressif chip.

It simply packages `esptool.py` with your binaries/flash_args (from your build).

This action will upload the resultant executable to the Github Action Job, and
(if triggered from release) to the release as well.

The primary use case for this action is to be run on releases, so that the
executable will be automatically generated and added to the release for ease of
use.

```yaml
  package:
    name: Package the binaries into an executables for Windows, MacOS, and Linux (Ubuntu)
    needs: build
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: esp-cpp/esp-packaged-programmer-action@v1.0.5
        with:
          zipfile-name: 'your-build-artifacts'
          programmer-name: 'your_programmer_name'
```

> NOTE: you can use either `zipfile-name` or `zipfile-id` as input to this
> script. If you are using MATRIX strategy (for which you may struggle to get
> the zipfile id output for each step), you may want to use the `zipfile-name`
> instead.

See the example in [Using this action](#using-this-action) for a more complete
example showing how to build your code and zip it for use by this action.

### Required Build Artifacts

It requires:
- firmware.bin (or whatever the name of your project is, e.g. <project-name>.bin)
- bootloader.bin
- partition-table.bin
- flasher_args.json

### Optional Build Artifacts

May optionally contain filesystem binaries and associated -flash_args files such as:
- littlefs.bin
- littlefs-flash_args

It also supports other partition image data such as
- ota_data_initial.bin

## Using this action

Below is an example workflow file that:

1. Builds the binaries using esp-idf's github action `espressif/esp-idf-ci-action`
2. Zips the binaries and flash args into a single archive, uploading it for other jobs to use
3. Runs this action (`esp-cpp/esp-packaged-programmer-action`) to build those
   binaries into executable flashing programs for `windows`, `macos`, and
   `linux`.

In the example below, we are using the `zipfile-id` input and hard-linking that
to the `build` job output. You could instead use the `zipfile-name` input and
provide it the name of the artifact (`firmware`) in this case.

```yaml
on: 
  push:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:

jobs:
  # this would be your normal build job to build your esp binaries
  build:
    runs-on: ubuntu-latest
    name: Build the binaries and upload them for packaging
    # you need this to link the zip file name to the packaging job(s)
    outputs:
      zipfile-id: ${{ steps.zip_step.outputs.artifact-id }}
    steps:
      - uses: actions/checkout@v4
      - name: Build the code
        uses: espressif/esp-idf-ci-action@v1
          with:
          esp_idf_version: v5.4.1
          target: esp32s3
          path: '.'
          command: idf.py build
      - name: Upload build files in a single zip
        id: zip_step
        uses: actions/upload-artifact@v4
        with:
          name: 'firmware'
          path: |
            build/*.bin
            build/*.elf
            build/bootloader/bootloader.bin
            build/partition_table/partition-table.bin
            build/flasher_args.json
            build/flash_args
            build/*-flash_args

  package:
    name: Package the binaries into an executables for Windows, MacOS, and Linux (Ubuntu)
    needs: build
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: esp-cpp/esp-packaged-programmer-action@v1.0.5
        with:
          zipfile-id: ${{ needs.build.outputs.zipfile-id }}
          programmer-name: 'your_programmer_name'
          exclude-file-globs: '*.elf, app-flash_args, bootloader-flash_args, partition-table-flash_args'
```

### Inputs

```yaml
- uses: esp-cpp/download-artifact@v1.0.5
  with:
    # The ID of the artifact to download. 
    # Mutually exclusive with `zipfile-name`. 
    # The artifact should be a zip that contains the files and folder 
    # structure of the build output. Can be created by passing relevant 
    # files to the actions/upload-artifact@v4 action.
    zipfile-id:

    # The name of the artifact to download. 
    # Mutually exclusive with `zipfile-id`. 
    # The artifact should be a zip that contains the files and folder 
    # structure of the build output. Can be created by passing relevant 
    # files to the actions/upload-artifact@v4 action.
    zipfile-name:

    # The base name of the programmer executable. 
    # Will have version tag (e.g. v1.0.0 or commit hash if no tags) and 
    # OS suffix (e.g. windows, macos, linux) added to it.
    programmer-name:

    # Comma-separated list of file names or globs which are present in 
    # the zipfile but which should be excluded from the packaging. 
    exclude-file-globs:
```
