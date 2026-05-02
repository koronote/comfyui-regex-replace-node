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
        if not prompt or '%' not in prefix:
            return prefix

        try:
            if hasattr(prompt, 'original_prompt'):
                items = prompt.original_prompt.items()
            elif hasattr(prompt, 'items'):
                items = prompt.items()
            else:
                return prefix

            node_map: dict = {}
            for _, node_data in items:
                if not isinstance(node_data, dict):
                    continue
                class_type = node_data.get("class_type", "")
                inputs = node_data.get("inputs", {})
                if class_type:
                    node_map.setdefault(class_type, []).append(inputs)

            def replace_node_ref(m: re.Match) -> str:
                node_type   = m.group(1)
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
