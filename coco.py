#! /usr/bin/python3
import time
import json
from pathlib import Path


class COCOAnnotation:
    """ Create COCO Annotation. 
    According to the format definition on official website, each attribute has dependency to the:
        info -> None
        category -> None
        license -> None
        image -> license
        annotation -> category, image
    If you are adding new data, you should follow the steps below.
        self.new_info()
        self.new_category()
        self.new_license()
        self.new_image()
        self.new_polygon()

    Args:
            src_path (Path): root path of the source images.
            dst_path (Path): root path of the coco dataset. eg. coco
    """

    def date_str(self) -> str:
        return time.strftime("%Y/%m/%d", time.localtime())

    def datetime_str(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def __init__(self, src_path: Path, dst_path: Path):
        """
        Create COCO Annotation Generator

        Args:
            src_path (Path): root path of the source images.
            dst_path (Path): root path of the coco dataset. eg. coco
        """
        self.data = {
            "info": {
                "year":  time.localtime().tm_year,
                "version": "0.0",
                "description": "No description",
                "contributor": "Unknown",
                "url": "https://cocodataset.org/",
                "date_created": self.date_str(),
            },
            "images": [],
            "categories": [],
            "annotations": [],
            "licenses": [
                {
                    "id": 1,
                    "name": "Attribution-NonCommercial-ShareAlike License",
                    "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
                }
            ]
        }
        self.scale = 1.0
        self.src_path = src_path
        self.dst_path = dst_path

    def set_image_scale(self, scale: float):
        """
        Set the output image scale.
        In case you want to scale the image and polygons.

        Args:
            scale (float): (w_out, h_out) = (w_in, h_in)*scale
        """
        self.scale = scale

    def save(self, path: Path):
        with path.open('w') as f:
            json.dump(self.data, f)

    def load(self, path: Path):
        with path.open('r') as f:
            self.data = json.load(f)

    def get_info(self) -> dict:
        return self.data['info']

    def new_info(self, version: str, description="No description",
                 contributor="Unknown", url="https://cocodataset.org/",
                 year=time.localtime().tm_year, date_created=date_str()):
        self.data['info'] = {
            "year":  year,
            "version": version,
            "description": description,
            "contributor": contributor,
            "url": url,
            "date_created": date_created,
        }

    def query_license(self, name: str):
        return [lc for lc in self.data['licenses'] if lc['name'] == name]

    def new_license(self, name: str, url: str):
        # reject duplicated data
        result = self.query_license(name)
        if len(result) > 0:
            return result[0]
        # create new license
        new_id = len(self.data['licenses']) + 1
        new_license = {
            "id": new_id,
            "name": name,
            "url": url
        }
        self.data['licenses'].append(new_license)
        return new_license

    def query_category(self, name: str):
        return [cat for cat in self.data['categories'] if cat['name'] == name]

    def new_category(self, name: str, super_cat: str):
        # reject duplicated data
        result = self.query_category(name)
        if len(result) > 0:
            return result[0]
        # create new category
        new_id = len(self.data['categories']) + 1
        category = {"id": new_id,
                    "name": name,
                    "supercategory": super_cat}
        self.data['categories'].append(category)
        return category

    def new_polygon(self, image_id: int, category_id: int, polygons: list):

        # reject non-exsistent category
        if len(self.data['categories']) < category_id:
            raise ValueError("category number does not exist")

        # reject non-exsistent image
        if len(self.data['images']) < image_id:
            raise ValueError("image_idr does not exist")

        new_id = len(self.data['annotations']) + 1
        is_crowd = 0
        area = sum(poly2area(poly) for poly in polygons)
        bbox = poly2bbox(polygons)
        annotation = {
            "id": new_id,
            "image_id": image_id,
            "category_id": category_id,
            "segmentation": polygons,
            "area": area,
            "bbox": bbox,
            "iscrowd": is_crowd
        }
        self.data['annotations'].append(annotation)
        return annotation

    def query_image(self, file_name: str) -> list:
        return [img for img in self.data['images'] if img['file_name'] == file_name]

    def new_image(self, file_name: str,
                  license=1,
                  flickr_url="https://www.flickr.com/",
                  coco_url="https://cocodataset.org/",
                  data_captured=None
                  ):
        if data_captured == None:
            data_captured = self.datetime_str()
        # reject duplicated data
        result = self.query_image(file_name)
        if len(result) > 0:
            return result[0]

        # Reject non-existent license ID
        if len(self.data['licenses']) < license:
            raise ValueError("license number does not exist")

        # open, resize,rename, and save the image
        new_id = len(self.data['images']) + 1
        img = Image.open(self.src_path / file_name)
        img_resized = img.resize((int(img.width * self.scale),
                                  int(img.height * self.scale)))
        # add scale string to the file name
        fn = Path(file_name)
        file_name = fn.stem + "_{}".format(self.scale) + fn.suffix
        # save
        img_resized.save(self.dst_path/"images"/file_name)

        # create new coco image annotation
        image = {
            "id": new_id,
            "width": img_resized.width,
            "height": img_resized.height,
            "file_name": file_name,
            "license": license,
            "flickr_url": flickr_url,
            "coco_url": coco_url,
            "date_captured": data_captured
        }
        self.data['images'].append(image)
        return image
