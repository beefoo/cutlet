## Met collections

Retrieve images

```
python scripts/get_met_images.py -query "`Object Name` == \"Sculpture\"" -out "output/met-sculptures/"
python scripts/get_met_images.py -query "`Object Name` == \"Statuette\"" -out "output/met-statuettes/"
python scripts/get_met_images.py -query "`Object Name` == \"Figure\"" -out "output/met-figures/"
python scripts/get_met_images.py -query "`Object Name` == \"Head\"" -out "output/met-heads/"
python scripts/get_met_images.py -query "`Object Name` == \"Bust\"" -out "output/met-busts/"
python scripts/get_met_images.py -query "`Object Name` == \"Figurine\"" -out "output/met-figurines/"
python scripts/get_met_images.py -query "`Object Name` == \"Mask\"" -out "output/met-masks/"
python scripts/get_met_images.py -query "`Object Name` == \"Toy\"" -out "output/met-toys/"
python scripts/get_met_images.py -query "`Object Name` == \"Ornament\"" -out "output/met-ornaments/"
python scripts/get_met_images.py -query "`Object Name` == \"Textile\"" -out "output/met-textiles/"
```

Segment images

```
python scripts/segment_images.py -in "output/select-met-figures/*.jpg" -out "output/figures-segments/" -edge 0 -composite bbox -rml -clean
```

## LoC collections

- [Historic American Buildings Survey/Historic American Engineering Record/Historic American Landscapes Survey (query:"Color Transparencies", original-format:photo, print, drawing, online-format:image)](https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-records/?c=150&fa=original-format:photo,+print,+drawing&q=Color+Transparencies&sp=3&st=list)
- [William P. Gottlieb Collection (original-format:photo, print, drawing)](https://www.loc.gov/collections/jazz-photography-of-william-p-gottlieb/?fa=original-format:photo,+print,+drawing)
- [Musical Instruments at the Library of Congress (original-format:3d object)](https://www.loc.gov/collections/musical-instruments-at-the-library-of-congress/?fa=original-format:3d+object)
- [Martha Graham at the Library of Congress (original-format:photo, print, drawing, online-format:image)](https://www.loc.gov/collections/martha-graham/?fa=original-format:photo,+print,+drawing%7Conline-format:image)
- [Larry Colwell Dance Photographs, 1944-1966 (original-format:photo, print, drawing)](https://www.loc.gov/collections/larry-colwell-dance-photographs-1944-to-1966/?fa=original-format:photo,+print,+drawing)

## SI Collections 

- [Cultery at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B2%5D=object_type%3A%22Cutlery%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Furniture at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B2%5D=object_type%3A%22Furniture%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Buttons at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=object_type%3A%22Button%22&edan_fq%5B2%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Paintings at the National Portrait Gallery](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANPG%20OR%20unit_code%3ANPG_BL%20OR%20unit_code%3ANPG_PC%20OR%20unit_code%3ANPG_YT&edan_fq%5B1%5D=object_type%3A%22Paintings%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
- [Activism at NMAAHC](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANMAAHC%20OR%20unit_code%3ANMAAHC_YT&edan_fq%5B1%5D=topic%3A%22Activism%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
- [Aircraft at the Air and Space Museum](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANASM%20OR%20unit_code%3ANASMAC%20OR%20unit_code%3ANASM_BL%20OR%20unit_code%3ANASM_YT&edan_fq%5B1%5D=object_type%3A%22Aircraft%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
