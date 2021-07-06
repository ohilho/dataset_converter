#! /usr/bin/python3


def poly2area(polygon: list) -> float:
    """ This is realiztion of shoelace method.
    This method works only for one polygon.
    This method does not work on self intersecting polygons.
    (because this is a special case of Green theorm)

    Args:
        polygon (list): [x1,y1,x2,y2,...] or [[x11,y11,x12,y12,...],[x21,y21,x22,y22,...]]
    """
    # There should be 3 points at leat to make an area.
    if len(polygon) < 6:
        return 0
    arr = np.array(polygon).reshape((-1, 2))
    arr = np.concatenate([arr[-1, :].reshape((1, 2)), arr], axis=0)
    pos = np.sum(arr[:-1, 0] * arr[1:, 1])
    neg = np.sum(arr[:-1, 1] * arr[1:, 0])
    area = np.abs(pos - neg)*0.5
    return area


def poly2bbox(polygon: list) -> list:
    """ Find a bounding box from polygon points.
    Bounding box representation is [x,y,width,hight],
    where x and y are the coordinate of top left corner.

    Args:
        polygon (list): [x1,y1,x2,y2,...]
    """
    arr = np.array(polygon).reshape((-1, 2))
    max_xy = np.max(arr, axis=0)
    min_xy = np.min(arr, axis=0)
    w_h = max_xy - min_xy
    return [min_xy[0], min_xy[1], w_h[0], w_h[1]]
