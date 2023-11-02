"""
Inkycal ePaper driving functions
Copyright by aceisace
"""
import os
import logging
from importlib import import_module
from PIL import Image

from inkycal.custom import top_level
import glob

def import_driver(model):
    return import_module(f'inkycal.display.drivers.{model}')

class Display:
    """Display class for inkycal

    Creates an instance of the driver for the selected E-Paper model and allows
    rendering images and calibrating the E-Paper display

    Args:
      - epaper_model: The name of your E-Paper model.

    """

    def __init__(self, epaper_model):
        """Load the drivers for this epaper model"""

        if 'colour' in epaper_model:
            self.supports_colour = True
        else:
            self.supports_colour = False

        try:
            driver = import_driver(epaper_model)
            self._epaper = driver.EPD()
            self.model_name = epaper_model

        except ImportError:
            raise Exception('This module is not supported. Check your spellings?')

        except FileNotFoundError:
            raise Exception('SPI could not be found. Please check if SPI is enabled')

    def render(self, im_black: Image.Image, im_colour=Image.Image or None) -> None:
        """Renders an image on the selected E-Paper display.

        Initlializes the E-Paper display, sends image data and executes command
        to update the display.

        Args:
          - im_black: The image for the black-pixels. Anything in this image that is
            black is rendered as black on the display. This is required and ideally
            should be a black-white image.

          - im_colour: For E-Paper displays supporting colour, a separate image,
            ideally black-white is required for the coloured pixels. Anything that is
            black in this image will show up as either red/yellow.

        Rendering an image for black-white E-Paper displays:

        >>> sample_image = Image.open('path/to/file.png')
        >>> display = Display('my_black_white_display')
        >>> display.render(sample_image)


        Rendering black-white on coloured E-Paper displays:

        >>> sample_image = Image.open('path/to/file.png')
        >>> display = Display('my_coloured_display')
        >>> display.render(sample_image, sample_image)


        Rendering coloured image where 2 images are available:

        >>> black_image = Image.open('path/to/file.png') # black pixels
        >>> colour_image = Image.open('path/to/file.png') # coloured pixels
        >>> display = Display('my_coloured_display')
        >>> display.render(black_image, colour_image)
        """

        epaper = self._epaper

        if not self.supports_colour:
            print('Initialising..', end='')
            epaper.init()
            print('Updating display......', end='')
            epaper.display(epaper.getbuffer(im_black))
            print('Done')

        elif self.supports_colour:
            if not im_colour:
                raise Exception('im_colour is required for coloured epaper displays')
            print('Initialising..', end='')
            epaper.init()
            print('Updating display......', end='')
            epaper.display(epaper.getbuffer(im_black), epaper.getbuffer(im_colour))
            print('Done')

        print('Sending E-Paper to deep sleep...', end='')
        epaper.sleep()
        print('Done')

    def calibrate(self, cycles=3):
        """Calibrates the display to retain crisp colours

        Flushes the selected display several times with it's supported colours,
        removing any previous effects of ghosting.

        Args:
          - cycles: -> int. The number of times to flush the display with it's
            supported colours.

        It's recommended to calibrate the display after every 6 display updates
        for best results. For black-white only displays, calibration is less
        critical, but not calibrating regularly results in grey-ish text.

        Please note that calibration takes a while to complete. 3 cycles may
        take 10 minutes on black-white E-Papers while it takes 20 minutes on coloured
        E-Paper displays.
        """

        epaper = self._epaper
        epaper.init()

        display_size = self.get_display_size(self.model_name)

        white = Image.new('1', display_size, 'white')
        black = Image.new('1', display_size, 'black')

        print('----------Started calibration of ePaper display----------')
        if self.supports_colour:
            for _ in range(cycles):
                print('Calibrating...', end=' ')
                print('black...', end=' ')
                epaper.display(epaper.getbuffer(black), epaper.getbuffer(white))
                print('colour...', end=' ')
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(black))
                print('white...')
                epaper.display(epaper.getbuffer(white), epaper.getbuffer(white))
                print(f'Cycle {_ + 1} of {cycles} complete')

        if not self.supports_colour:
            for _ in range(cycles):
                print('Calibrating...', end=' ')
                print('black...', end=' ')
                epaper.display(epaper.getbuffer(black))
                print('white...')
                epaper.display(epaper.getbuffer(white)),
                print(f'Cycle {_ + 1} of {cycles} complete')

            print('-----------Calibration complete----------')
            epaper.sleep()

    @classmethod
    def get_display_size(cls, model_name):
        """Returns the size of the display as a tuple -> (width, height)

        Looks inside "drivers" folder for the given model name, then returns it's
        size.

        Args:
          - model_name: str -> The name of the E-Paper display to get it's size.

        Returns:
          (width, height) ->tuple, showing the size of the display

        You can use this function directly without creating the Display class:

        >>> Display.get_display_size('model_name')
        """
        try:
            driver = import_driver(model_name)
            return driver.EPD_WIDTH, driver.EPD_HEIGHT
        except Exception as e:
            logging.error(f'Failed to load driver for ${model_name}. Check spelling?')
            raise e;

    @classmethod
    def get_display_names(cls) -> list:
        """Prints all supported E-Paper models.

        Fetches all filenames in driver folder and prints them on the console.

        Returns:
          Printed version of all supported Displays.

        Use one of the models to intilialize the Display class in order to gain
        access to the E-Paper.

        You can use this function directly without creating the Display class:

        >>> Display.get_display_names()
        """
        driver_files = top_level + '/inkycal/display/drivers/'
        drivers = [i for i in os.listdir(driver_files) if i.endswith(".py") and not i.startswith("__") and "_" in i]
        return drivers


if __name__ == '__main__':
    print("Running Display class in standalone mode")
