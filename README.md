# ARAMCON 2 Badge Firmware

The main firmware code for the ARAMCON 2 Badge. For documentation, see [https://badge.a-combinator.com](the Badge's doc site).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

1. Copy the content of this folder to your badge drive. You can skip the `.git` directory.
2. Install the [required libraries](requirements.txt). The recommended way is to use the [CircUp package manager](https://learn.adafruit.com/keep-your-circuitpython-libraries-on-devices-up-to-date-with-circup/install-circup):

```
circup install -r requirements.txt
```

Alternatively, download the lastest [CircuitPython Bundle 6.x Package](https://circuitpython.org/libraries), extract it, and copy the `lib` folder to your badge drive.

## License

Released under [the MIT License](LICENSE).
