# AramCon 2 Badge Firmware

The main firmware code for the AramCon 2 Badge.

## Installation

1. Copy the content of this folder to your badge drive. You can skip the `.git` directory.
2. Install the [required libraries](requirements.txt). The recommended way is to use the [CircUp package manager](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup):

    ```
    circup install --py -r requirements.txt
    ```

    Alternatively, download the lastest [CircuitPython Bundle 6.x Package](https://circuitpython.org/libraries), extract it, and copy the `lib` folder to your badge drive.
