import numpy as np

DATA_TYPE_TRANSFORM = np.dtype({
    'names': [
        'x', 'y', 'scale', 'rotation'],
    'formats': [
        np.float16, np.float16, 
        np.float16, np.float16],
    'offsets': [
        0, 2, 
        4, 6],
    'itemsize': 8})

DATA_TYPE_VERTEX = np.dtype({
    'names': [
        'imageSize_x','imageSize_y',
        'texoffset_x','texoffset_y', 'layer',
        'center_x', 'center_y', 
        'scale', 'rotation'],
    'formats': [
        np.float16, np.float16, 
        np.float16, np.float16, np.uint8, 
        np.float16, np.float16, 
        np.float16, np.float16],
    'offsets': [
        0, 2, 
        4, 6, 8, 
        9, 11, 
        13, 15],
    'itemsize': 17})