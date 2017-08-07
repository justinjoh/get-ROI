## get-ROI
Used to segment fluorescence microscopy images of a chemoflux device

#### Input data:
Each image should contain the same number of whole channels. Designed such that rotation, scaling, and absolute 
image intensity should not matter.

##### Current difficulties:
Will not work correctly in "early-stage" growth (when bacteria do not fill significant portion of chamber)

Has trouble dealing with overlaying text (not an issue in raw images)

#### Usage:
Put .py files in same directory as the images from the time-lapse sequence.

Run as:

$ python main.py #chambers save_folder

Where #chambers is the number of chambers in each image and save_folder is the folder to be created with the 
segmented chamber images inside.

###### Created in the Lambert Lab (Cornell University, Department of Applied and Engineering Physics)
