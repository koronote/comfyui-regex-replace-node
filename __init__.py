import re
import time
from nodes import SaveImage  # type: ignore[import]


class SaveImageWithWeight(SaveImage):
    CATEGORY = "image"
    FUNCTION = "save_images_with_weight"

    @classmethod
    def INPUT_TYPES(cls):
        inputs = super().INPUT_TYPES()
        inputs["required"]["lora_weight"] = ("STRING", {"default": "", "multiline": False})
        return inputs

    @staticmethod
    def _apply_date_vars(prefix: str) -> str:
        now = time.localtime()

        def format_date(fmt: str) -> str:
            # yyyy を先に置換して yy との二重マッチを防ぐ。MM（月）は mm（分）より先に処理する。
            result = fmt
            result = result.replace("yyyy", f"{now.tm_year:04d}")
            result = result.replace("yy",   f"{now.tm_year % 100:02d}")
            result = result.replace("MM",   f"{now.tm_mon:02d}")
            result = result.replace("dd",   f"{now.tm_mday:02d}")
            result = result.replace("hh",   f"{now.tm_hour:02d}")
            result = result.replace("mm",   f"{now.tm_min:02d}")
            result = result.replace("ss",   f"{now.tm_sec:02d}")
            return result

        prefix = re.sub(r'%date:([^%]+)%', lambda m: format_date(m.group(1)), prefix)
        prefix = re.sub(r'%date%',         lambda _: format_date("yyyyMMddhhmmss"), prefix)
        return prefix

    @staticmethod
    def _apply_node_vars(prefix: str, prompt) -> str:
        """%NodeType.widgetName% をプロンプト内のノードのウィジェット値に置換する。
        フロントエンドの SaveImageExtraOutput 拡張は既知ノードのみを処理するため、
        カスタムノードではサーバー側で代替処理が必要。"""
        if not prompt or '%' not in prefix:
            return prefix

        try:
            # DynamicPrompt または plain dict の両方に対応
            if hasattr(prompt, 'original_prompt'):
                items = prompt.original_prompt.items()
            elif hasattr(prompt, 'items'):
                items = prompt.items()
            else:
                return prefix

            # class_type → inputs のリストを構築
            node_map: dict = {}
            for _, node_data in items:
                if not isinstance(node_data, dict):
                    continue
                class_type = node_data.get("class_type", "")
                inputs = node_data.get("inputs", {})
                if class_type:
                    node_map.setdefault(class_type, []).append(inputs)

            def replace_node_ref(m: re.Match) -> str:
                node_type  = m.group(1)
                widget_name = m.group(2)
                for inputs in node_map.get(node_type, []):
                    val = inputs.get(widget_name)
                    # リンク値は [node_id, slot] のリストで格納されるためスキップ
                    if val is not None and not isinstance(val, list):
                        return str(val)
                return m.group(0)

            return re.sub(r'%([^%.]+)\.([^%]+)%', replace_node_ref, prefix)
        except Exception:
            return prefix

    def save_images_with_weight(self, images, filename_prefix="ComfyUI", lora_weight="", prompt=None, extra_pnginfo=None):
        filename_prefix = filename_prefix.replace("%LoraWeight%", lora_weight)
        filename_prefix = self._apply_date_vars(filename_prefix)
        filename_prefix = self._apply_node_vars(filename_prefix, prompt)
        return super().save_images(images=images, filename_prefix=filename_prefix, prompt=prompt, extra_pnginfo=extra_pnginfo)


class RegexReplaceNode:
    """
    複数の文字列入力をマージし、正規表現にマッチした部分を削除するノード。
    入力数は input_count ウィジェットで可変。
    """

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
        # text_1 〜 text_{input_count} を順番に収集
        texts = []
        for i in range(1, input_count + 1):
            t = kwargs.get(f"text_{i}") or ""
            if t.strip():
                texts.append(t + "\n")

        merged = ",".join(texts)

        # 正規表現で置換
        if pattern.strip():
            try:
                replaced = re.sub(pattern, "", merged)
            except re.error:
                # 無効なパターンの場合はそのまま返す
                replaced = merged
        else:
            replaced = merged

        # 余分なスペースやカンマ、コメントアウト部分を削除
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
