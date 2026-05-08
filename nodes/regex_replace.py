import re
import unicodedata


class RegexReplaceNode:
    CATEGORY = "text"
    OUTPUT_NODE = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("結果テキスト",)
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_count": ("INT", {"default": 4, "min": 1, "step": 1, "display": "number"}),
                "pattern":     ("STRING", {"default": "", "multiline": False}),
                "deduplicate": ("BOOLEAN", {"default": False}),
            },
        }

    def execute(self, input_count, pattern, deduplicate=False, **kwargs):
        texts = []
        for i in range(1, input_count + 1):
            t = kwargs.get(f"text_{i}") or ""
            t = unicodedata.normalize("NFKC", t)
            if t.strip():
                texts.append(t + "\n")

        merged = ",".join(texts)

        if merged.startswith("{"):
            replaced = merged   # JSON形式の場合は正規表現を適用せず、そのまま返す
        else:

            if pattern.strip():
                try:
                    replaced = re.sub(pattern, "", merged)
                except re.error:
                    replaced = merged
            else:
                replaced = merged

            replaced = re.sub(r'/\*.*?\*/', "", replaced)
            replaced = re.sub(r'//.*|#.*|\n', ",", replaced)
            replaced = re.sub(r'\s{2,}', " ", replaced)
            replaced = re.sub(r',\s+', ",", replaced)
            replaced = re.sub(r'\s+,', ",", replaced)
            replaced = re.sub(r',\s*,', ",", replaced)
            replaced = re.sub(r',{2,}', ",", replaced)
            replaced = re.sub(r', ', ",", replaced)

            if deduplicate:
                tags = [tag.strip() for tag in replaced.split(",")]
                seen = set()
                unique_tags = []
                for tag in tags:
                    if tag and tag not in seen:
                        seen.add(tag)
                        unique_tags.append(tag)
                replaced = ",".join(unique_tags)

        replaced = re.sub(r'BREAK', "\nBREAK,\n", replaced)

        return {
            "ui": {"text": [merged, replaced]},
            "result": (replaced,),
        }
