# ESP Packaged Programmer Action

This repository provides a reusable action for turning your esp-idf binaries
into executables which program the esp chip. It may work for other platforms on
espressif chips such as Arduino / Platform.IO, but I have not designed / tested
it with those environments.

The output of this action is a binary which requires no other dependencies,
files, or installation, but allows anyone to flash your code onto the
appropriate espressif chip.

It simply packages `esptool.py` with your binaries/flash_args (from your build).

It requires:
- firmware.bin (or whatever the name of your project is, e.g. <project-name>.bin)
- bootloader.bin
- partition-table.bin
- flasher_args.json

May optionally contain filesystem binaries and associated -flash_args files such as:
- littlefs.bin
- littlefs-flash_args

## Using this action

Below is an example workflow file that:

1. Builds the binaries using esp-idf's github action `espressif/esp-idf-ci-action`
2. Zips the binaries and flash args into a single archive
3. Uploads the zip file for other jobs to use
4. Runs this action (`esp-cpp/esp-packaged-programmer-action`) to build those
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
      zipfile: ${{ steps.zip_step.outputs.zipfile }}
    steps:
      - uses: actions/checkout@v4
      - name: Build the code
        uses: espressif/esp-idf-ci-action@v1
          with:
          esp_idf_version: v5.4.1
          target: esp32s3
          path: '.'
          command: idf.py build
    # TODO: you should change the zip name here to be what you want
    # TODO: you should update the binaries and such that are flashed to match what you need
    - name: Zip up build files to be downloaded by the packagers
      id: zip_step
      run: |
        zip_name="your_firmware_name_$(git describe --tags --dirty).zip"
        zip -r -j $zip_name build/your_firmware_name.bin build/your_firmware_name.elf build/bootloader/bootloader.bin build/partition_table/partition-table.bin build/littlefs.bin build/ota_data_initial.bin build/flasher_args.json build/littlefs-flash_args
        echo "artifact_name=$zip_name" >> "$GITHUB_ENV"
        echo "zipfile=$zip_name" >> "$GITHUB_OUTPUT"
    - name: Upload zipped build files
      uses: actions/upload-artifact@v4
      with:
        name: ${{ env.artifact_name }}
        path: ${{ env.artifact_name }}

  # Add this if you want to package the binaries into an executable for Windows
  package_windows:
    needs: build
    runs-on: windows-latest
    name: Package the binaries into an executable for Windows Systems
    steps:
      - uses: esp-cpp/esp-packaged-programmer-action@v1
        id: windows-package
        with:
          zipfile-name: ${{ needs.build.outputs.zipfile }}
          # NOTE: you can provide your own name here. default is 'programmer'. 
          #       Will be appended with git version and platform.
          programmer-name: 'custom_programmer'

  # Add this if you want to package the binaries into an executable for MacOS
  package_macos:
    needs: build
    runs-on: macos-latest
    name: Package the binaries into an executable for MacOS Systems
    steps:
      - uses: esp-cpp/esp-packaged-programmer-action@v1
        id: macos-package
        with:
          zipfile-name: ${{ needs.build.outputs.zipfile }}
          # NOTE: you can provide your own name here. default is 'programmer'. 
          #       Will be appended with git version and platform.
          programmer-name: 'custom_programmer'

  # Add this if you want to package the binaries into an executable for Linux
  package_linux:
    needs: build
    runs-on: ubuntu-latest
    name: Package the binaries into an executable for Linux systems
    steps:
      - uses: esp-cpp/esp-packaged-programmer-action@v1
        id: linux-package
        with:
          zipfile-name: ${{ needs.build.outputs.zipfile }}
          # NOTE: you can provide your own name here. default is 'programmer'. 
          #       Will be appended with git version and platform.
          programmer-name: 'custom_programmer'
      # Example of how you can use the artifact name in a subsequent step or script
      - run: echo artifact-name "$ARTIFACT_NAME"
        shell: bash
        env:
          RANDOM_NUMBER: ${{ steps.linux-package.outputs.artifact-name }}
```

