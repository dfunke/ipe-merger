# Original author: Simon Fink
# Additional contributions: Daniel Funke

import argparse
import xml.etree.ElementTree as ET


def save_bitmaps(root, gBitmaps):
    
    # the ID for new bitmap objects
    nextID = 1
    if gBitmaps:
        nextID = max(gBitmaps) + 1

    LIDtoBitmap = {} # local ID to bitmap
    LIDtoGID = {} # local ID to global ID

    for bitmap in root.iterfind(f".//bitmap"):
        lid = int(bitmap.get("id"))
        LIDtoBitmap[lid] = bitmap
        LIDtoGID[lid] = lid

    for lID, lBitmap in LIDtoBitmap.items():
        
        found = False
        for gID, gBitmap in gBitmaps.items():
            if gBitmap.text == lBitmap.text:
                # the bitmap is already present in the file, don't add it again
                # map the local ID to the existing global ID
                LIDtoGID[lID] = gID
                found = True
                break

        if not found:
            # its a new bitmap, add it to the global structure with the next available ID
            newGID = nextID
            nextID = nextID + 1
            lBitmap.set("id", str(newGID))
            gBitmaps[newGID] = lBitmap
            LIDtoGID[lID] = newGID # update local ID to global ID mapping

    for image in root.iterfind(f".//image"):
        image.set("bitmap", str(LIDtoGID[int(image.get("bitmap"))]))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Takes multiple xml ipe files as input and merges them into a single file. '
                    'Optionally only retains pages containing a certain symbol.'
    )

    parser.add_argument('outfile')
    parser.add_argument('infile', nargs="+", type=ET.parse)
    parser.add_argument('-s', '--symbol',
                        help="Only include pages that contain a symbol with this name.")
    parser.add_argument('-t', '--template', type=ET.parse,
                        help="The ipe file whose styles should be used for the output file. Defaults to the first input file.")

    args = parser.parse_args()

    bitmaps = {}
    for doc in args.infile:
        save_bitmaps(doc.getroot(), bitmaps)

    docs = [doc.getroot().findall("page") for doc in args.infile]
    if args.symbol:
        docs = [[page for page in doc if page.find(f".//use[@name='{args.symbol}']") is not None]
                for doc in docs]

    templ = args.template or args.infile[0]
    troot = templ.getroot()
    for obj in troot.findall("page"):
        troot.remove(obj)
    for obj in troot.findall("bitmap"):
        troot.remove(obj)

    templ.getroot().extend(bitmaps.values())
    for pages in docs:
        templ.getroot().extend(pages)
    if not any(docs):
        print("No pages generated!")

    templ.write(args.outfile, encoding="unicode")
