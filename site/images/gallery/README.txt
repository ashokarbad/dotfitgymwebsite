ADDING PHOTOS
=============

1. Put the photo in the folder that matches the activity, e.g.
      trekking/trekking-01.webp
      yoga/yoga-morning-flow-01.webp

2. From the project root, run:
      python3 tools/scan_gallery.py

3. Upload the site folder. The photo now appears in the gallery page,
   in the matching activity's own gallery, and in the lightbox.

Filenames become the photo title, so name them properly:
      yoga-sunrise-class-01.webp   ->  "Yoga sunrise class"
      IMG_4821.jpg                 ->  "Img 4821"      (don't)

Formats: .webp preferred, .jpg and .png also work.
Size:    about 1600px on the long edge, under 300 KB.
         Compress at squoosh.app before adding.

Titles, dates and captions can be set precisely in a captions.json
file inside the folder. See trekking/captions.json for the shape.

Photos of identifiable members need their permission before they go up.
