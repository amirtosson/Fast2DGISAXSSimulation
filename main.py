"""
@author:    Amir Tosson
@license:   GNU General Public License v3 or higher
@copyright: Universität Siegen, Deutschland
@email:     tosson@physik.uni-siegen.de
"""

"""
summary:    The main  

name:       main

date:       08-06-2021

"""

import SimulationControls as _sim
import csv
import numpy as np
import concurrent.futures
import timeit as process_time


def TaoDispersionRand():
    # TaO dispersion [0.6e-5    -   2.0e-5]
    return np.random.randint(6, 21) * 1e-06


def TaoAbsorptionRand():
    # TaO absorption [1e-8    -    9e-6]
    return np.random.randint(1, 900) * 1e-08


def TaDispersionRand():
    # TaO dispersion [1e-5    -   4e-5]
    return np.random.randint(1, 5) * 1e-05


def TaAbsorptionRand():
    # Ta absorption [1e-8    -    9e-6]
    return np.random.randint(1, 900) * 1e-08


def Cu3NDispersionRand():
    # TaO dispersion [0.8e-5    -   3.0e-5]
    return np.random.randint(8, 31) * 1e-06


def Cu3NAbsorptionRand():
    # TaO absorption [1e-8    -    9e-6]
    return np.random.randint(1, 900) * 1e-08


def ThicknessRand():
    return 0.4 * np.random.randint(1, 10)


def GenerateRandomData(numLayers):
    """
    Description
    -----------
    It generates random numbers for Dispersion, Absorption , and Thickness
    of different layers

    Parameters
    ----------
    numLayers : TYPE int
                DESCRIPTION the number of the layers

    Returns
    -------
    dispersionData : TYPE array of float
                     DESCRIPTION the random dispersion data of the layers

    thicknessData : TYPE array of float
                     DESCRIPTION the random thickness data of the layers

    absorptionData : TYPE array of float
                     DESCRIPTION the random absorption data of the layers
    """

    dispersionSwitcher = {0: TaoDispersionRand, 1: TaDispersionRand, 2: Cu3NDispersionRand}
    absorptionSwitcher = {0: TaoAbsorptionRand, 1: TaAbsorptionRand, 2: Cu3NAbsorptionRand}

    dispersionData = [0] * numLayers
    thicknessData = [0] * numLayers
    absorptionData = [0] * numLayers
    for i in range(numLayers):
        func = dispersionSwitcher.get(i % 3)
        func2 = absorptionSwitcher.get(i % 3)
        dis_h = func()
        thi_h = ThicknessRand()
        absor_h = func2()
        dispersionData[i] = dis_h
        thicknessData[i] = thi_h
        absorptionData[i] = absor_h

    return dispersionData, thicknessData, absorptionData


def StartGISAXSSimulation(numberOfDatasets):
    GISAXS_simulation = _sim.SimulationControls()
    for imgNum in range(numberOfDatasets):
        # Random layers number between 1 to 12
        layerNumber = np.random.randint(1, 13)
        arrDispersion, arrThickness, arrAbsorption = GenerateRandomData(layerNumber)
        """
        You can manually overwrite any random array of dispersion, thickness or/and absorption. 
        Just uncomment the following line/s and put your data. Be sure that it has the same size as the layer number:
        arrDispersion = [1,2,3,4,5,6,48,79,564,7]
        arrThickness = [1,2,3,4,5,6,48,79,564,7]
        arrAbsorption = [1,2,3,4,5,6,48,79,564,7]
        """
        Img = GISAXS_simulation.StartSim(imgNum, layerNumber, arrThickness, arrDispersion, arrAbsorption)

        """
        This will save all data images with a separating col contains -1  
        """
        with open('InputData_All.csv', 'a', encoding='UTF8', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerow([-1])
            writer.writerows(Img)
        fd.close()

        """
        # use this if you want to save each image in a separated file
        with open('InputData_'+ str(imgNum) +'.csv', 'a', encoding='UTF8', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerows(Img)
        fd.close()
        """


if __name__ == '__main__':
    # how many images you want to simulate (can be changed)
    numberOfImages = 5

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(StartGISAXSSimulation, int(numberOfImages/4) + 1) for x in range(4)]
