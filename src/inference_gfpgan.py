from PIL import Image
import os
from io import BytesIO
import numpy as np

from gfpgan import GFPGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from torch.cuda import is_available as cudaIsAvailable
from torch.backends.mps import is_available as mpsIsAvailable


def upscale_image(image_data: BytesIO, upscale: int = 2):
    arch = 'clean'
    channel_multiplier = 2
    model_name = 'GFPGANv1.4'
    url = 'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth'

    # determine model paths
    model_path = os.path.join('experiments/pretrained_models', model_name + '.pth')
    if not os.path.isfile(model_path):
        model_path = os.path.join('gfpgan/weights', model_name + '.pth')
    if not os.path.isfile(model_path):
        # download pre-trained models from url
        model_path = url

    _half = True
    if cudaIsAvailable():
        backend_type = 'cuda'
        print("Running on CUDA")
    elif mpsIsAvailable():
        backend_type = 'mps'
        print("Running on Apple NPU")
    else:
        print("Running on CPU")
        backend_type = 'cpu'
        _half = False

    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
    bg_upsampler = RealESRGANer(
        scale=2,
        model_path='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth',
        model=model,
        tile=400,
        tile_pad=10,
        pre_pad=0,
        device=backend_type,
        half=_half)  # need to set False in CPU mode

    restorer = GFPGANer(
        model_path=model_path,
        upscale=upscale,
        arch=arch,
        channel_multiplier=channel_multiplier,
        bg_upsampler=bg_upsampler)

    # ------------------------ restore ------------------------
    im_src = Image.open(image_data)
    im_converted = im_src.convert(mode="RGB")
    im_np = np.asarray(im_converted)
    im_np = im_np[:, :, ::-1]

    # restore faces and background if necessary
    _, _, restored_img = restorer.enhance(
        im_np,
        has_aligned=False,
        only_center_face=False,
        paste_back=True,
        weight=0.5)

    # save restored img
    restored_img = restored_img[:, :, ::-1]
    im = Image.fromarray(restored_img)
    result = BytesIO()

    im.save(result, format=im_src.format)
    result.seek(0)
    return result
