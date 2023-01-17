import argparse
import xml.etree.ElementTree as ET


def save_bitmaps(root, bitmaps):
    offset = len(bitmaps)
    bitmaps.extend(root.findall("bitmap"))

    for bitmap in root.iterfind(f".//bitmap"):
        bitmap.set("id", str(int(bitmap.get("id")) + offset))

    for image in root.iterfind(f".//image"):
        image.set("bitmap", str(int(image.get("bitmap")) + offset))


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
                        help="The ipe file whose styles should be used for the output file. Defaults to the last input file.")

    args = parser.parse_args()

    bitmaps = []
    for doc in args.infile:
        save_bitmaps(doc.getroot(), bitmaps)

    docs = [doc.getroot().findall("page") for doc in args.infile]
    if args.symbol:
        docs = [[page for page in doc if page.find(f".//use[@name='{args.symbol}']") is not None]
                for doc in docs]

    templ = args.template or args.infile[-1]
    troot = templ.getroot()
    for obj in troot.findall("page"):
        troot.remove(obj)
    for obj in troot.findall("bitmap"):
        troot.remove(obj)

    templ.getroot().extend(bitmaps)
    for pages in docs:
        templ.getroot().extend(pages)
    if not any(docs):
        print("No pages generated!")

    templ.write(args.outfile, encoding="unicode")
