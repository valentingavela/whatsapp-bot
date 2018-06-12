import os
import glob
from PIL import Image
from pathlib import Path

os.chdir('/home/wasap/whatsapp-bot/all_media/')

# # get all the jpg files from the current folder
for infile in glob.glob("*.jpg"):
    if infile[0:3] != "qr-":
        if not Path("thumbs/T_" + str(infile)).is_file():
            print("Creating thumbnail")
            im = Image.open(infile).convert('RGB')
            # convert to thumbnail image
            im.thumbnail((512, 512), Image.ANTIALIAS)
            # don't save if thumbnail already exists
            # if infile[0:2] != "T_":
            # prefix thumbnail file with T_
            im.save("thumbs/T_" + infile, "JPEG")
        else:
            print("File exists")


# # get all the jpg files from the current folder
for infile in glob.glob("*.png"):
    if not Path("thumbs/T_" + str(infile)).is_file():
        print("Creating thumbnail")
        im = Image.open(infile).convert('RGBA')
        # convert to thumbnail image
        im.thumbnail((512, 512), Image.ANTIALIAS)
        # don't save if thumbnail already exists
        # if infile[0:2] != "T_":
        # prefix thumbnail file with T_
        im.save("thumbs/T_" + infile, "PNG")
    else:
         print("File exists")

