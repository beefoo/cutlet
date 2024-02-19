## Met collections

### Get stats

Create .csv containing counts for different columns from the [MetObjects data](https://github.com/metmuseum/openaccess/raw/master/MetObjects.csv)

```
python scripts/get_stats.py -src "cache/met-open-access-objects/MetObjects.csv" -query "`Is Public Domain`" -cols "Object Name,Medium" -out "output/stats_met_{id}.csv"
```

### Retrieve images

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

### Segment images

Some are run twice with a second pass with reduced image size to account for images that get a runtime error `nonzero is not supported for tensors with more than INT_MAX elements`

```
python scripts/segment_images.py -in "output/select-met-figures/*.jpg" -out "output/figures-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/select-met-heads/*.jpg" -out "output/heads-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/select-met-heads/*.jpg" -out "output/heads-segments/" -edge 0 -composite bbox -rml -maxd 3000
python scripts/segment_images.py -in "output/select-met-animals/*.jpg" -out "output/animals-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/select-met-animals/*.jpg" -out "output/animals-segments/" -edge 0 -composite bbox -rml -maxd 3000
```

## LoC collections

### Sample queries

- [WPA Posters](https://www.loc.gov/collections/works-progress-administration-posters/?st=list&c=150)
- [Historic American Buildings Survey/Historic American Engineering Record/Historic American Landscapes Survey (query:"Color Transparencies", original-format:photo, print, drawing, online-format:image)](https://www.loc.gov/collections/historic-american-buildings-landscapes-and-engineering-records/?c=150&fa=original-format:photo,+print,+drawing&q=Color+Transparencies&st=list)
- [William P. Gottlieb Collection (original-format:photo, print, drawing)](https://www.loc.gov/collections/jazz-photography-of-william-p-gottlieb/?fa=original-format:photo,+print,+drawing)
- [Musical Instruments at the Library of Congress (original-format:3d object)](https://www.loc.gov/collections/musical-instruments-at-the-library-of-congress/?fa=original-format:3d+object)
- [Martha Graham at the Library of Congress (original-format:photo, print, drawing, online-format:image)](https://www.loc.gov/collections/martha-graham/?fa=original-format:photo,+print,+drawing%7Conline-format:image)
- [Larry Colwell Dance Photographs, 1944-1966 (original-format:photo, print, drawing)](https://www.loc.gov/collections/larry-colwell-dance-photographs-1944-to-1966/?fa=original-format:photo,+print,+drawing)

### Download and segment images

```
python scripts/get_images.py -src "data/loc/musical-instruments-at-the-library-of-congress-original-format-3d-object-2024-01-28.csv" -image "image_url" -out "output/loc-instruments/loc-{id}.jpg"
python scripts/segment_images.py -in "output/select-loc-instruments/*.jpg" -out "output/flute-segments/" -edge 0 -composite bbox -rml
```

### Download high-res images and segment text

```
python scripts/get_loc_images.py -src "data/loc/posters-wpa-posters-2024-02-11.csv" -out "output/loc-posters/"
python scripts/segment_image_text.py -in "output/loc-posters/*.jpg" -out "output/poster-text-segments/"
```

### Download high-res images

```
python scripts/get_loc_images.py -src "data/loc/loc-item-selections-2024-02-18-194519.csv" -out "output/loc-selections/"
```

## SI Collections

### Sample queries

- [Cultery at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B2%5D=object_type%3A%22Cutlery%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Furniture at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B2%5D=object_type%3A%22Furniture%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Buttons at Cooper Hewitt](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ACHNDM%20OR%20unit_code%3ACHNDM_BL%20OR%20unit_code%3ACHNDM_YT&edan_fq%5B1%5D=object_type%3A%22Button%22&edan_fq%5B2%5D=set_name%3A%22Product%20Design%20and%20Decorative%20Arts%20Department%22&edan_fq%5B3%5D=media_usage%3A%22CC0%22)
- [Paintings at the National Portrait Gallery](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANPG%20OR%20unit_code%3ANPG_BL%20OR%20unit_code%3ANPG_PC%20OR%20unit_code%3ANPG_YT&edan_fq%5B1%5D=object_type%3A%22Paintings%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
- [Activism at NMAAHC](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANMAAHC%20OR%20unit_code%3ANMAAHC_YT&edan_fq%5B1%5D=topic%3A%22Activism%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
- [Aircraft at the Air and Space Museum](https://www.si.edu/search/collection-images?edan_q=&edan_fq%5B0%5D=unit_code%3ANASM%20OR%20unit_code%3ANASMAC%20OR%20unit_code%3ANASM_BL%20OR%20unit_code%3ANASM_YT&edan_fq%5B1%5D=object_type%3A%22Aircraft%22&edan_fq%5B2%5D=media_usage%3A%22CC0%22)
- [Gems at the Natural History Museum](https://www.si.edu/search/collection-images?edan_q=&edan_fq[]=unit_code:NAA+OR+unit_code%3ANMNH+OR+unit_code%3ANMNHANTHRO+OR+unit_code%3ANMNHBIRDS+OR+unit_code%3ANMNHBOTANY+OR+unit_code%3ANMNHENTO+OR+unit_code%3ANMNHFISHES+OR+unit_code%3ANMNHHERPS+OR+unit_code%3ANMNHINV+OR+unit_code%3ANMNHMAMMALS+OR+unit_code%3ANMNHMINSCI+OR+unit_code%3ANMNHPALEO+OR+unit_code%3ANMNH_BL+OR+unit_code%3ANMNH_PC+OR+unit_code%3ANMNH_YT+OR+unit_code%3ACEPH+OR+unit_code%3AHSFA+OR+unit_code%3AHSFA_YT+OR+unit_code%3AMMAM+OR+unit_code%3ANMNHEDUCATION&edan_fq[]=set_name:%22Gems%22&edan_fq[]=media_usage:%22CC0%22)

### Download data

To get a list of department datasets:

```
aws s3 ls --no-sign-request s3://smithsonian-open-access/metadata/edan/
```

Then download each department dataset:

```
python scripts/get_si_data.py -src "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/chndm/index.txt" -cache "cache/si-chndm/" -out "output/si-chndm-pd.csv"
python scripts/get_si_data.py -src "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/nmaahc/index.txt" -cache "cache/si-nmaahc/" -out "output/si-nmaahc-pd.csv"
python scripts/get_si_data.py -src "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/nasm/index.txt" -cache "cache/si-nasm/" -out "output/si-nasm-pd.csv"
python scripts/get_si_data.py -src "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/nmnhminsci/index.txt" -cache "cache/si-nmnhminsci/" -out "output/si-nmnhminsci-pd.csv"
```

### Generate counts

```
python scripts/get_stats.py -src "output/si-chndm-pd.csv" -cols "group,object_type,object_type_2,object_type_3" -out "output/stats_si_chndm_{id}.csv"
python scripts/get_stats.py -src "output/si-nmaahc-pd.csv" -cols "group,object_type,object_type_2,object_type_3" -out "output/stats_si_nmaahc_{id}.csv"
python scripts/get_stats.py -src "output/si-nasm-pd.csv" -cols "group,object_type,object_type_2,object_type_3" -out "output/stats_si_nasm_{id}.csv"
python scripts/get_stats.py -src "output/si-nmnhminsci-pd.csv" -cols "group,topic" -out "output/stats_si_nmnhminsci_{id}.csv"
```

### Download images

```
python scripts/get_images.py -src "output/si-chndm-pd.csv" -image "image" -query "object_type == \"Cutlery\" or object_type_2 == \"Cutlery\" or object_type_3 == \"Cutlery\"" -out "output/si-cutlery/si-{id}.jpg"
python scripts/get_images.py -src "output/si-chndm-pd.csv" -image "image" -query "object_type == \"Button\" or object_type_2 == \"Button\" or object_type_3 == \"Button\"" -out "output/si-buttons/si-{id}.jpg"
python scripts/get_images.py -src "output/si-chndm-pd.csv" -image "image" -query "object_type == \"Furniture\" or object_type_2 == \"Furniture\" or object_type_3 == \"Furniture\"" -out "output/si-furniture/si-{id}.jpg"
python scripts/get_images.py -src "output/si-nasm-pd.csv" -image "image" -query "object_type == \"Aircraft\" or object_type_2 == \"Aircraft\" or object_type_3 == \"Aircraft\"" -out "output/si-aircraft/si-{id}.jpg"
python scripts/get_images.py -src "output/si-nmnhminsci-pd.csv" -image "image" -query "group == \"Gems\"" -out "output/si-gems/si-{id}.jpg"
```

### Segment images

Some are run twice with a second pass with reduced image size to account for images that get a runtime error `nonzero is not supported for tensors with more than INT_MAX elements`

```
python scripts/segment_images.py -in "output/si-cutlery/*.jpg" -out "output/cutlery-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/si-buttons/*.jpg" -out "output/buttons-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/select-si-furniture/*.jpg" -out "output/furniture-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/si-aircraft/*.jpg" -out "output/aircraft-segments/" -edge 0 -composite bbox -rml
python scripts/segment_images.py -in "output/si-gems/*.jpg" -out "output/gems-segments/" -edge 0 -composite bbox -rml
```
