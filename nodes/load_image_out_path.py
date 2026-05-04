from nodes import LoadImage  # type: ignore[import]
import folder_paths


class LoadImageOutPath(LoadImage):
    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "path")
    FUNCTION = "load_image_with_path"

    def load_image_with_path(self, image):
        image_tensor, mask = super().load_image(image)
        image_path = folder_paths.get_annotated_filepath(image).replace("\\", "/")
        image_path += "\n\n"
        return (image_tensor, mask, image_path)
