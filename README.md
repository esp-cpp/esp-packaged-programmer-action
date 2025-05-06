# ESP Packaged Programmer Action

This repository provides a reusable action for turning your esp-idf binaries
into executables which program the esp chip. It may work for other platforms on
espressif chips such as Arduino / Platform.IO, but I have not designed / tested
it with those environments.

## Using this action

```yaml
on: [push]

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
      - name: Upload Packaged Executable (Windows)
        uses: actions/upload-artifact@v4
          with:
            name: ${{ steps.windows-package.outputs.artifact-name }}
            path: ${{ steps.windows-package.outputs.artifact-name }}

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
      - name: Upload Packaged Executable (MacOS)
        uses: actions/upload-artifact@v4
          with:
            name: ${{ steps.macos-package.outputs.artifact-name }}
            path: ${{ steps.macos-package.outputs.artifact-name }}

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
      - run: echo random-number "$RANDOM_NUMBER"
        shell: bash
        env:
          RANDOM_NUMBER: ${{ steps.foo.outputs.random-number }}
      - name: Upload Packaged Executable (Linux)
        uses: actions/upload-artifact@v4
          with:
            name: ${{ steps.linux-package.outputs.artifact-name }}
            path: ${{ steps.linux-package.outputs.artifact-name }}
```

