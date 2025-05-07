# ESP Packaged Programmer Action

This repository provides a reusable action for turning your esp-idf binaries
into executables which program the esp chip. It may work for other platforms on
espressif chips such as Arduino / Platform.IO, but I have not designed / tested
it with those environments.

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

### Required Build Outputs

It requires:
- firmware.bin (or whatever the name of your project is, e.g. <project-name>.bin)
- bootloader.bin
- partition-table.bin
- flasher_args.json

### Optional Build Outputs

May optionally contain filesystem binaries and associated -flash_args files such as:
- littlefs.bin
- littlefs-flash_args

## Using this action

Below is an example workflow file that:

1. Builds the binaries using esp-idf's github action `espressif/esp-idf-ci-action`
2. Zips the binaries and flash args into a single archive, uploading it for other jobs to use
3. Runs this action (`esp-cpp/esp-packaged-programmer-action`) to build those
   binaries into executable flashing programs for `windows`, `macos`, and
   `linux`.

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
      - uses: esp-cpp/esp-packaged-programmer-action@v1
        with:
          zipfile-id: ${{ needs.build.outputs.zipfile-id }}
          programmer-name: 'your_programmer_name'
```

