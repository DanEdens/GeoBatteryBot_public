import argparse
import errno
import os
import shutil
import subprocess
import sys
import webbrowser
from typing import List
from typing import Optional
from webbrowser import open

import pyqrcode
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
        {'linux': 'xdg-open', 'win32': 'explorer', 'darwin': 'open'}[
            sys.platform]
    subprocess.run([image_viewer_command, path])


def copy_to_clipboard(text: str) -> Optional[None]:
    """
    Copies the given text to the system clipboard.
    :param text: The text to be copied to the clipboard.
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


def clean_target_dir(first_id: int, last_id: int) -> None:
    """
    Remove the directory with the specified name and create a new, empty one in its place.

    Parameters:
    - first_id: The first ID of the range of IDs for which the directory should be created.
    - last_id: The last ID of the range of IDs for which the directory should be created.

    Returns:
    - None
    """
    dir_name = f"{first_id}-{last_id}"
    if os.path.exists(dir_name):
        raise OSError(f"Directory '{dir_name}' already exists")
    try:
        shutil.rmtree(dir_name)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.makedirs(dir_name)
    os.chdir(dir_name)


def generate_qr_code(id: str = "1") -> Optional[str]:
    """
    Generates QR codes for webhook URLs for a given ID. The ID is padded with zeros to 5 digits.
    :param id: The ID to use in the webhook URLs and QR codes.
    :return: The padded ID.
    """
    padded_id = id.rjust(5, '0')
    url_in = f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?" \
             f"apikey={args.apikey}&deviceNames=GeoBatteryBot&text=" \
             f"battery%3D%3A%3D{padded_id}%3D%3A%3DIn"
    url_out = f"https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?" \
              f"apikey={args.apikey}&deviceNames=GeoBatteryBot&text=" \
              f"battery%3D%3A%3D{padded_id}%3D%3A%3DOut"
    qr_code_in = pyqrcode.create(url_in)
    print(f"Generating {padded_id}..")
    with open(f'{padded_id}_In.png', 'wb') as f:
        qr_code_in.png(f, scale=10)
    qr_code_out = pyqrcode.create(url_out)
    with open(f'{padded_id}_Out.png', 'wb') as f:
        qr_code_out.png(f, scale=10)
    return padded_id


def label_qr_code(padded_id: str, state: str) -> Optional[None]:
    """
    Labels QR code images with their ID and state, and adds a border to the images.
    :param padded_id: The padded ID to be used for labeling the images.
    :param state: The state to be used for labeling the images.
    :return: None
    """
    temp_file = f'{padded_id}_{state}.png'
    qr_in = Image(filename=temp_file)
    with Drawing() as draw:
        draw.font_size = 45
        draw.font_weight = 700
        draw.text(240, 32, f'{padded_id} - Check {state}')
        draw(qr_in)
        qr_in.border('White', int(5), int(20))
        qr_in.save(filename=temp_file)


def composite_v(images: List[str], id: str) -> Optional[str]:
    """
    Merges In and Out QR code images into a single image.
    :param images: The QR code images to be merged.
    :param id: The ID to be used for the merged image.
    :return: The file path of the merged image.
    """
    with Image() as output:
        output.blank(1530, 780)
        in_image = Image(filename=f'{id}_In.png')
        out_image = Image(filename=f'{id}_Out.png')
        output.composite(in_image, 0, 15)
        output.composite(out_image, 760, 15)
        output.rotate(270)
        output.save(filename=f'{id}.png')
        return f'{id}.png'


def composite_hz(images: List[str]) -> Optional[str]:
    """
    Merges all QR code image pairs into a single image.
    :param images: The QR code image pairs to be merged.
    :return: The file path of the merged image.
    """
    print(f'Using images: {images}')
    with Image() as output:
        w = 5
        count = len(images)
        output.blank(780 * count, 1520)
        for i in range(count):
            each_image = Image(filename=images[i])
            output.composite(each_image, w, 5)
            w = w + (each_image.width + 50)
        final_path = f'{args.output}\\final{args.firstID}-{args.lastID}.png'
        ensure_exists(final_path)
        output.save(filename=final_path)
        return final_path


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
    clean_target_dir(FirstID, LastID)
    images = []

    for each in range(FirstID, LastID + 1):
        paddedId = generate_qr_code(each)
        label_qr_code(paddedId, 'In')
        label_qr_code(paddedId, 'Out')
        images.append(composite_v(images, paddedId))
    finalPath = composite_hz(images)
    if args.show:
        open_image(finalPath)
    if args.clip:
        copy_to_clipboard(finalPath)
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
    if not args.firstID:
        args.firstID = int(input("Enter your First ID: "))
    if not args.lastID:
        args.lastID = int(input("Enter your Last ID: "))
    main(args.firstID, args.lastID)
