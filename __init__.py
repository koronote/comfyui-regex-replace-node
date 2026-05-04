from .nodes.regex_replace import RegexReplaceNode
from .nodes.text_display import TextDisplayNode
from .nodes.save_image_with_weight import SaveImageWithWeight
from .nodes.load_image_out_path import LoadImageOutPath

NODE_CLASS_MAPPINGS = {
    "RegexReplaceNode": RegexReplaceNode,
    "TextDisplayNode": TextDisplayNode,
    "SaveImageWithWeight": SaveImageWithWeight,
    "LoadImageOutPath": LoadImageOutPath,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegexReplaceNode": "Regex Replace",
    "TextDisplayNode": "Text Display",
    "SaveImageWithWeight": "Save Image With Weight",
    "LoadImageOutPath": "Load Image (Out Path)",
}

WEB_DIRECTORY = "./web/js"
