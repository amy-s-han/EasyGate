#!/usr/bin/env python
import numpy as np
import cv2
from utils import SingleCameraHardware

if __name__ == "__main__":

	sourceTop = SingleCameraHardware(0) # Init top camera
	sourceTop.loadCalibrationData()

	while True:

		sourceTop.update(Display=True)

		if cv2.waitKey(1) == 113:
			break

	sourceTop.release()
