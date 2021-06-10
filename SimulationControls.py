"""
@author:    Amir Tosson
@license:   GNU General Public License v3 or higher
@copyright: Universität Siegen, Deutschland
@email:     tosson@physik.uni-siegen.de
"""

"""
summary:    this model contains the APIs of the 
            BornAgain-based simulation for GISAXS 

name:       SimulationControls

date:       08-06-2021

"""

import bornagain as ba
from bornagain import deg, nm
import csv


class SimulationControls():

    def __init__(self):
        super().__init__


    def InitBeam(self):
        """
       Description
       -----------
       It initializes the beam

       Parameters
       ----------

       Returns
       -------
       beam : TYPE bornAgain.beam structure
              DESCRIPTION the used beam
       """
        direction = ba.Direction(0.64 * deg, 0.0 * deg)
        beam = ba.Beam(1e+16 * 0.3 / 80, 0.14073 * nm, direction)
        return beam


    def InitDetector(self):
        """
       Description
       -----------
       It initializes the detector

       Parameters
       ----------

       Returns
       -------
       detector : TYPE bornAgain.detector structure
              DESCRIPTION the used detector
       """
        detector = ba.RectangularDetector(512, 26.6, 1024, 51.2)
        detector.setResolutionFunction(ba.ResolutionFunction2DGaussian(0.02, 0.02))
        detector.setPerpendicularToReflectedBeam(1277.0, 10.75, 20.65)
        return detector


    def InitSim(self, _sample, _beam, _detector):
        """
         Description
         -----------
         It initializes the simulation

         Parameters
         ----------
        _beam : TYPE bornAgain.beam structure
                 DESCRIPTION the used detector

        _sample : TYPE bornAgain.sample structure
                 DESCRIPTION the used sample

        _detector : TYPE bornAgain.detector structure
                     DESCRIPTION the used detector
         Returns
         -------
         sim : TYPE bornAgain.simulation structure
                    DESCRIPTION the simulation
        """

        sim = ba.GISASSimulation(_beam, _sample, _detector)
        sim.getOptions().setUseAvgMaterials(True)
        sim.getOptions().setIncludeSpecular(True)
        background = ba.ConstantBackground(5e+01)
        sim.setBackground(background)
        return sim


    def InitSample(self, imgNum=0, numLayers=1, ThiDataUser=0, DisDataUser=0, AbsorUserData=0):
        """
        Description
        -----------
        It initializes the sample

        Parameters
        ----------
        imgNum : TYPE int
               DESCRIPTION dataset ID

        numLayers : TYPE int
                   DESCRIPTION the number of the layers

        DisDataUser : TYPE array of float
                         DESCRIPTION the random dispersion data of the layers

        ThiDataUser : TYPE array of float
                         DESCRIPTION the random thickness data of the layers

        AbsorUserData : TYPE array of float
                         DESCRIPTION the random absorption data of the layers

        Returns
        -------
        multiLayer : TYPE bornAgain.multiLayer structure
                  DESCRIPTION the multiLayer definition of the sample
        """

        # Defining constant materials
        materialAir = ba.HomogeneousMaterial("Air",     0.0,                0.0)
        materialSiO2 = ba.HomogeneousMaterial("SiO2",    5.93e-06,       7.42e-08)
        materialSubstrate = ba.HomogeneousMaterial("Substrate", 6.31e-06,     1.21e-07)

        # Defining constant Layers
        layerAir = ba.Layer(materialAir)
        layerSiO2 = ba.Layer(materialSiO2, 100)
        layerSubstrate = ba.Layer(materialSubstrate, 500)

        # Defining Roughness of constant layers
        layerRoughnessSiO2 = ba.LayerRoughness(0.54, 0.6, 30.0 * nm)
        layerRoughnessSubstrate = ba.LayerRoughness(0.54, 0.6, 30.0 * nm)

        # Defining layers roughness
        layersRoughness = [ba.LayerRoughness(0.46, 0.6, 30.0 * nm), ba.LayerRoughness(0.39, 0.6, 30.0 * nm), ba.LayerRoughness(0.57, 0.6, 30.0 * nm)]

        # Defining layers names
        layersNames = ["TaO", "Ta", "Cu3N"]

        """
        Saving output data in one file:
        first col is the number of layers followed by the dispersion, absorption, and thickness data. 
        example: 3 layers -> 10 cols
        col1 = number of layers     
        col2 = 1st layer dispersion     
        col3 = 2nd layer dispersion        
        col4 = 3rd layer dispersion        
        col5 = 1st layer absorption        
        col6 = 2nd layer absorption        
        col7 = 3rd layer absorption        
        col8 = 1st layer thickness        
        col9 = 2nd layer thickness        
        col10 = 3rd layer thickness        
        """
        with open('OutputData_All.csv', 'a', encoding='UTF8', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerow([numLayers] + DisDataUser + AbsorUserData + ThiDataUser)
        fd.close()

        multiLayer = ba.MultiLayer()
        multiLayer.setCrossCorrLength(2000)

        # Adding the Air layer
        multiLayer.addLayer(layerAir)

        for i in range(numLayers):
            material = ba.HomogeneousMaterial(layersNames[i % 3] + str(i), DisDataUser[i], AbsorUserData[i])
            layer = ba.Layer(material, ThiDataUser[i])
            layerRoughness = layersRoughness[i % 3]
            multiLayer.addLayerWithTopRoughness(layer, layerRoughness)

        # Adding the SiO2 layer
        multiLayer.addLayerWithTopRoughness(layerSiO2, layerRoughnessSiO2)

        # Adding the Substrate layer
        multiLayer.addLayerWithTopRoughness(layerSubstrate, layerRoughnessSubstrate)
        return multiLayer


    def RunSim(self, _simulation):
        """
         Description
         -----------
         It runs the simulation

         Parameters
         ----------
         _simulation : TYPE bornAgain.simulation structure
                        DESCRIPTION the simulation

         Returns
         -------
         hist.array() : numpy 2D array
                        DESCRIPTION the 2D image
        """
        _simulation.getOptions().setUseAvgMaterials(True)
        _simulation.getOptions().setIncludeSpecular(False)
        background = ba.ConstantBackground(5e+01)
        _simulation.runSimulation()
        result = _simulation.result()
        hist = result.histogram2d(ba.Axes.QSPACE)
        return hist.array()


    def StartSim(self, imgNum=0, numLayers=1, ThiDataUser=0, DisDataUser=0, AbsorUserData=0):
        """
        Description
        -----------
        The user callable function. It gets the user data and drives the simulation

        Parameters
        ----------
        imgNum : TYPE int
               DESCRIPTION dataset ID

        numLayers : TYPE int
                   DESCRIPTION the number of the layers

        DisDataUser : TYPE array of float
                         DESCRIPTION the random dispersion data of the layers

        ThiDataUser : TYPE array of float
                         DESCRIPTION the random thickness data of the layers

        AbsorUserData : TYPE array of float
                         DESCRIPTION the random absorption data of the layers

        Returns
        -------
        the results as numpy array
        """
        return self.RunSim(self.InitSim(self.InitSample(imgNum, numLayers, ThiDataUser, DisDataUser, AbsorUserData), self.InitBeam(),
                                        self.InitDetector()))


