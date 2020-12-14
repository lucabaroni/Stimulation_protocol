# Stimulation_protocol

## Overview of the stimulation
Each stimulation protocol consists in the presentation of a set of natural images and of drifting grating stimuli.
* Each drifting grating stimuli is presented 10 times. 
* A subset of the images is presented 10 times (repeated images)
* The rest of the images are presented only once (unique images)

###### _(temporary solution, later this will change)_ 
To simplify the experimental procedure the experiment 
is divided in 10 section.
* The same repeated images and drifting grating stimuli are presented once in every section of the experiment, so that
after the 10th section these stimuli are presented 10 times.
* The unique images changes over every sections, so that after the 10th section these stimuli are presented only once

Stimuli are displayed by the `utils.display_stimuli(..., utils.SignFunc)`, which take as last parameter a signaling
function to call when the window is flipped (i.e. when stimulus is presented) with
```python
win.callOnFlip(MySignFunc, frameInfo, clock)
```
Currently the functions called is `utils.SignFunc()` which takes as arguments the frameInfo dictionary and a clock
to store timestamps each frame presentation.

## Usage
Firstly set the parameters in `params_stim.txt` according to needs.

```python
{
    "stim_duration": 0.5, #in seconds
    "blank_duration": 5, #in seconds

    "size_of_stimuli" : 10, #in degree of visual field

    "images_path": "./images/life_of_animals", 
    "Nrepeated": 40, #number of images repeated over sections
    "Nunique": 60,  #number of images not repeated over sections

    "sf_grating": [0.01, 0.02, 0.04, 0.08, 0.16, 0.32], #spatial frequency of grating stimuli in cycles per degree
    "Nori_grating": 16 # number of different orientation of visual stimuli
    "size_grating" : 200 # temporarely needs to be adjusted by hand to have fullscreen grating stimuli (units=deg)
}
```

then run the script
```bash
python StimProtocol.py
```
Before showing stimuli `StimProtocol.py` asks through a dialogue box experiment informations 
and monitor name and distance.

The experiment information are used to construct the structure of the data folder. 

If the monitor name is not found among the ones already used, the user will be asked to insert details
of the monitor.

## Logs
Data is stored in appropriate folder according to the experiment info.

Example: `data/mouse/mouse01/13-12-2020/section_1`

Inside the folder there are four json files:
* `monInfo.json` contains details about monitor used and its distance
* `param_stim.json` contains used parameters of stimulation
* `stimuli_in_order.json` contains a dictionary where id of stimuli (image_path or orientation
  and spatial frequency of drifting gratings) and whether each stimulus is repeated or not are saved
* `frameInfo.json` contain dictionary of detailed logs of stimulation protocol
    * timestamp of frame presentation
    * stimulus id of the stimulus presented in that specific frame (image_path or orientation, 
      spatial frequency **and phase** of drifting gratings)






