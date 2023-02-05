Assisted Bed Tram module for Klipper

Module to mimic Marlin's Assisted Bed Leveling tool, that uses probe to level your bed screws instead of trying to measure how many times you need to turn the knobs.


Broken as of v0.11.0-99-g56444815 


Usage:

Use ASSISTED_BED_TRAM command or BED_TRAM macro.

Module will measure offset at each screw, then hover over the screws with the lowest offset. Then turn the knobs to trigger probe, and move onto next screw. Repeat if needed.



Installation:

Include assisted_bed_tram.cfg to your config

Copy assisted_bed_tram.py to ./klipper/klippy/extras

Configure screws_tilt_adjust

https://www.klipper3d.org/Config_Reference.html#screws_tilt_adjust