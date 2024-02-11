from .imagefunc import *

any = AnyType("*")

class ImageMaskScaleAs:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(self):

        fit_mode = ['letterbox', 'crop', 'fill']
        method_mode = ['lanczos', 'bicubic', 'hamming', 'bilinear', 'box', 'nearest']

        return {
            "required": {
                "scale_as": (any, {}),
                "fit": (fit_mode,),
                "method": (method_mode,),
            },
            "optional": {
                "image": ("IMAGE",),  #
                "mask": ("MASK",),  #
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "BOX",)
    RETURN_NAMES = ("image", "mask", "original_size")
    FUNCTION = 'image_mask_scale_as'
    CATEGORY = '😺dzNodes/LayerUtility'
    OUTPUT_NODE = True

    def image_mask_scale_as(self, scale_as, fit, method,
                            image=None, mask = None,
                            ):
        if scale_as.shape[0] > 0:
            _asimage = tensor2pil(scale_as[0])
        else:
            _asimage = tensor2pil(scale_as)
        target_width, target_height = _asimage.size
        _mask = Image.new('L', size=_asimage.size, color='black')
        _image = Image.new('RGB', size=_asimage.size, color='black')
        orig_width = 4
        orig_height = 4
        resize_sampler = Image.LANCZOS
        if method == "bicubic":
            resize_sampler = Image.BICUBIC
        elif method == "hamming":
            resize_sampler = Image.HAMMING
        elif method == "bilinear":
            resize_sampler = Image.BILINEAR
        elif method == "box":
            resize_sampler = Image.BOX
        elif method == "nearest":
            resize_sampler = Image.NEAREST

        ret_images = []
        ret_masks = []
        
        if image is not None:
            for image in image:
                _image = tensor2pil(image).convert('RGB')
                orig_width, orig_height = _image.size
                _image = fit_resize_image(_image, target_width, target_height, fit, resize_sampler)
                ret_images.append(pil2tensor(_image))
        if mask is not None:
            for mask in mask:
                _mask = tensor2pil(mask).convert('L')
                orig_width, orig_height = _mask.size
                _mask = fit_resize_image(_mask, target_width, target_height, fit, resize_sampler).convert('L')
                ret_masks.append(image2mask(_mask))
        if len(ret_images) > 0 and len(ret_masks) >0:
            return (torch.cat(ret_images, dim=0), torch.cat(ret_masks, dim=0), [orig_width, orig_height],)
        elif len(ret_images) > 0 and len(ret_masks) == 0:
            return (torch.cat(ret_images, dim=0), None,)
        elif len(ret_images) == 0 and len(ret_masks) > 0:
            return (None, torch.cat(ret_masks, dim=0), [orig_width, orig_height],)
        else:
            return (None, None,)

NODE_CLASS_MAPPINGS = {
    "LayerUtility: ImageMaskScaleAs": ImageMaskScaleAs
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LayerUtility: ImageMaskScaleAs": "LayerUtility: ImageMaskScaleAs"
}