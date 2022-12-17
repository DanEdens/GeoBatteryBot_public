import argparse
import errno
import os
import shutil
import subprocess
import sys
from webbrowser import open
from typing import Optional

import pyqrcode
import pytest
from wand.drawing import Drawing
from wand.image import Image

version = 1.1
dir_path = os.path.dirname(os.path.realpath(__file__))

helpMsg = f""
f"\n    GeoBatteryBot - Version: {version}\n"
f"\nGeo-Insturments Internal Software"
f"\n"
f"\nGenerates QR code stickers for Geo-instruments battery tracking"

parser = argparse.ArgumentParser(
        description=helpMsg,
        prog='GeoBatteryBot',
        formatter_class=argparse.RawDescriptionHelpFormatter
        )

parser.add_argument('-F', '--firstid',
                    default=os.environ.get("BATTERYBOT_FIRSTID", False),
                    type=int,
                    metavar='',
                    help="First Battery ID to generate")

parser.add_argument('-L', '--lastid',
                    default=os.environ.get("BATTERYBOT_LASTID", False),
                    type=int,
                    metavar='',
                    help="Last Battery ID to generate")

parser.add_argument('-s', '--show', action='store_true',
                    default=os.environ.get("BATTERYBOT_SHOW", False),
                    help='Open final image in photo viewer')

parser.add_argument('--log', action='store_true',
                    default=os.environ.get("BATTERYBOT_LOG", False),
                    help='Pubs log message after generation')

parser.add_argument('-0', '--output',
                    default=f"{dir_path}\\_output",
                    type=str,
                    help='Choose location for output files'
                    )

parser.add_argument('--nocleanup', action='store_false',
                    default=os.environ.get("BATTERYBOT_CLEANUP", True),
                    help='Prevents Clean up of temp files')

parser.add_argument('-c', '--clip', action='store_true',
                    default=os.environ.get("BATTERYBOT_CLIP", False),
                    help='Copy final filepath to clipboard for easy importing')

parser.add_argument('--apikey',
                    default=os.environ.get("BATTERYBOT_APIKEY"),
                    help='Override LastID and generate this number of IDs starting from firstID')

args = parser.parse_args()


def open_image(path: str) -> Optional[None]:
    """
    Opens the image at the given file path using the default system image viewer.
    :param path: The file path of the image to be opened.
    :return: None
    """
    image_viewer_command = \
    {'linux': 'xdg-open', 'win32': 'explorer', 'darwin': 'open'}[sys.platform]
    subprocess.run([image_viewer_command, path])


def copyToClipBoard(text):
    """
    Copies text to system clipboard
    :param text:
    :return: None
    """
    command = 'echo | set /p nul=' + text.strip() + '| clip'
    os.system(command)


def ensure_exists(path: str) -> None:
    """Create the directory path if it does not exist.

    Parameters:
    path (str): The directory path to create.
    """
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        try:
            os.makedirs(dirname)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise


def cleanTargetDir(_firstId=args.firstID, _lastId=args.lastID):
    """
    Remove old folder and create a clean one
    :param _firstId:
    :param _lastId:
    :return: None
    """
    try:
        shutil.rmtree(f"{_firstId}-{_lastId}")
    except OSError as e:
        pass
    os.mkdir(f"{_firstId}-{_lastId}")
    os.chdir(f"{_firstId}-{_lastId}")


def generateQRcode(id="1"):
    """
    Generates webhook Urls and QR codes for a given ID.
    Returns ID with padded zeros as paddedID
    :param id:
    :return: paddedid
    """
    paddedid = str(id).rjust(5, '0')
    url_in = f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?apikey={args.apikey}&deviceNames=GeoBatteryBot&text=battery%3D%3A%3D{paddedid}%3D%3A%3DIn"
    url_out = f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?apikey={args.apikey}&deviceNames=GeoBatteryBot&text=battery%3D%3A%3D{paddedid}%3D%3A%3DOut"
    In_temp = pyqrcode.create(url_in)
    print(f"Generating {paddedid}..")
    with open(f'{paddedid}_In.png', 'wb') as f:
        In_temp.png(f, scale=10)
    Out_temp = pyqrcode.create(url_out)
    with open(f'{paddedid}_Out.png', 'wb') as f:
        Out_temp.png(f, scale=10)
    return paddedid


def labelQRcode(images, _paddedID, state):
    """
    Labels QR code images with their ID and state and adds a border
    :param images:
    :param _paddedID:
    :param state:
    :return: None
    """
    tempFile = f'{_paddedID}_{state}.png'
    QRin = Image(filename=tempFile)
    with Drawing() as draw:
        draw.font_size = 45
        draw.font_weight = 700
        draw.text(240, 32, f'{_paddedID} - Check {state}')
        draw(QRin)
        QRin.border('White', int(5), int(20))
        QRin.save(filename=tempFile)


def compositeV(images, Id):
    """
    Merges In and Out QR codes into single image
    :param images:
    :param Id:
    :return: {Id}.png
    """
    with Image() as output:
        output.blank(1530, 780)
        InImage = Image(filename=f'{Id}_In.png')
        OutImage = Image(filename=f'{Id}_Out.png')
        output.composite(InImage, 0, 15)
        output.composite(OutImage, 760, 15)
        output.rotate(270)
        output.save(filename=f'{Id}.png')
        return (f'{Id}.png')


def compositeHz(images):
    """
    Merges all QR pairs into single image
    :param images:
    :return: _finalpath
    """
    print(f'Using images: {images}')
    with Image() as output:
        w = 5
        count = len(images)
        output.blank(780 * count, 1520)
        for each in range(count):
            eachImage = Image(filename=images[each])
            output.composite(eachImage, w, 5)
            w = w + (eachImage.width + 50)
        _finalpath = f'{args.output}\\final{args.firstID}-{args.lastID}.png'
        ensure_exists(_finalpath)
        output.save(filename=_finalpath)
        return (_finalpath)


# content of test_class.py
class TestClass:
    def test_one(self, _firstID=1):
        assert _firstID >= 0

    def test_two(self, _firstID=1, _lastID=2):
        assert _lastID >= _firstID


def main(FirstID, LastID):
    """
    Geo-Insturments Internal Software
    Created by: Dan Edens
    Generates In/Out QR code label stickers for Battery tracking system
    """
    TestClass.test_one(FirstID)
    TestClass.test_two(FirstID, LastID)
    cleanTargetDir(FirstID, LastID)
    images = []

    for each in range(FirstID, LastID + 1):
        paddedId = generateQRcode(each)
        labelQRcode(images, paddedId, 'In')
        labelQRcode(images, paddedId, 'Out')
        images.append(compositeV(images, paddedId))
    finalPath = compositeHz(images)
    if args.show: open_image(finalPath)
    if args.clip: copyToClipBoard(finalPath)
    os.chdir('../')
    if args.nocleanup:
        try:
            shutil.rmtree(f"{args.firstID}-{args.lastID}")
        except OSError as e:
            pass
    if args.log:
        import time

        nowtime = time.strftime("%m-%d-%H00")
        webbrowser.open(
            f"http://3.134.3.199:9191/mqtt?topic=shop/batterytracker/generator&message={args.firstID}-{args.lastID} at {nowtime}")


if __name__ == "__main__":
    if not args.firstID: args.firstID = int(input("Enter your First ID: "))
    if not args.lastID: args.lastID = int(input("Enter your Last ID: "))
    main(first, last)
