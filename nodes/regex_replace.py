import re


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
            if t.strip():
                texts.append(t + "\n")

        merged = ",".join(texts)

        if pattern.strip():
            try:
                replaced = re.sub(pattern, "", merged)
            except re.error:
                replaced = merged
        else:
            replaced = merged

        replaced = re.sub('/\*.*?\*/', "", replaced)
        replaced = re.sub('//.*|#.*|\\n', "", replaced)
        replaced = re.sub('\s{2,}', " ", replaced)
        replaced = re.sub(',\s+', ",", replaced)
        replaced = re.sub('\s+,', ",", replaced)
        replaced = re.sub(',\s*,', ",", replaced)
        replaced = re.sub(',{2,}', ",", replaced)
        replaced = re.sub(', ', ",", replaced)

        if deduplicate:
            tags = [tag.strip() for tag in replaced.split(",")]
            seen = set()
            unique_tags = []
            for tag in tags:
                if tag and tag not in seen:
                    seen.add(tag)
                    unique_tags.append(tag)
            replaced = ",".join(unique_tags)

        return {
            "ui": {"text": [merged, replaced]},
            "result": (replaced,),
        }
