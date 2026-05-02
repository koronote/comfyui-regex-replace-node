from .nodes.regex_replace import RegexReplaceNode
from .nodes.text_display import TextDisplayNode
from .nodes.save_image_with_weight import SaveImageWithWeight

NODE_CLASS_MAPPINGS = {
    "RegexReplaceNode": RegexReplaceNode,
    "TextDisplayNode": TextDisplayNode,
    "SaveImageWithWeight": SaveImageWithWeight,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RegexReplaceNode": "Regex Replace",
    "TextDisplayNode": "Text Display",
    "SaveImageWithWeight": "Save Image With Weight",
}

WEB_DIRECTORY = "./web/js"
