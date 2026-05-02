class TextDisplayNode:
    CATEGORY = "text"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("テキスト",)
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
            },
        }

    def execute(self, text):
        return {
            "ui": {"text": [text]},
            "result": (text,),
        }
