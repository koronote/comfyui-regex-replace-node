# ComfyUI カスタムノード開発メモ

## 作成済みカスタムノード

### Regex Replace (`custom_nodes/regex_replace_node/`)

複数の文字列入力をマージし、正規表現にマッチした部分を削除するノード。

**ファイル構成:**
- `custom_nodes/regex_replace_node/__init__.py` — ノード本体
- `custom_nodes/regex_replace_node/web/js/regexReplace.js` — テキスト表示用フロントエンド拡張

#### 入力

| 名前 | 種類 | 必須 | 説明 |
|------|------|------|------|
| テキスト 1 | STRING (外部ノード接続) | 必須 | マージ対象のテキスト |
| テキスト 2〜N | STRING (外部ノード接続) | 任意 | マージ対象のテキスト（空の場合は除外） |
| input_count | INT (ウィジェット) | 必須 | 入力数（デフォルト: 4、最小: 1）。「入力数を更新」ボタンで反映 |
| pattern | STRING (ウィジェット) | 必須 | マッチした部分を削除する正規表現（空欄でスキップ） |
| deduplicate | BOOLEAN (ウィジェット) | 必須 | 重複タグを除去するかどうか（デフォルト: OFF） |

セパレーターは `","` 固定。ウィジェット表示順: `input_count` → `[更新ボタン]` → `pattern` → `deduplicate`

#### 出力

| 名前 | 種類 | 説明 |
|------|------|------|
| 結果テキスト | STRING | 正規表現置換後のテキスト |

#### UI表示

- ノード実行後に「マージ後テキスト」「置換後テキスト」の2つの読み取り専用ウィジェットをノード上に表示
- JS 拡張 (`regexReplace.js`) が `onExecuted` で `message.text[0]`（マージ後）と `message.text[1]`（置換後）を受け取り描画

#### 動作仕様

1. 空でない入力テキストを `","` でマージ
2. 正規表現パターンにマッチした箇所を `""` で削除
3. 無効な正規表現パターンが入力された場合は置換しない
4. コメント部分や余分なスペース、カンマを削除して整形
5. `deduplicate` が ON の場合、カンマ分割 → 各タグをトリム → 重複除去（順序保持）→ 再結合
6. マージ後と置換後のテキストをノード上に表示
7. 「入力数を更新」ボタンを押すと `input_count` の値に合わせて入力ソケットが追加・削除される

---

### Text Display (`custom_nodes/regex_replace_node/`)

1件のテキストを受け取り、ノード上に表示するノード。

**ファイル構成:**
- `custom_nodes/regex_replace_node/__init__.py` — `TextDisplayNode` クラス
- `custom_nodes/regex_replace_node/web/js/textDisplay.js` — フロントエンド拡張

#### 入力 / 出力

| 名前 | 種類 | 説明 |
|------|------|------|
| text | STRING (ウィジェット + ソケット接続可) | 表示するテキスト。直接入力も外部接続も可 |
| テキスト（出力） | STRING | 受け取ったテキストをそのまま出力 |

#### 動作仕様

- 実行後、`onExecuted` が `text` ウィジェットの値を接続元の値で更新する
- `%TextDisplayNode.text%` で SaveImage 等のファイル名プレフィックスから参照可能（ウィジェットに直接入力した固定値の場合のみ確実に動作）

---

### Save Image With Weight (`custom_nodes/regex_replace_node/`)

ComfyUI 標準の `SaveImage` を継承し、Lora の強度等を含む任意テキストをファイル名に埋め込めるようにしたノード。

**ファイル構成:**
- `custom_nodes/regex_replace_node/__init__.py` — `SaveImageWithWeight` クラス

#### 追加入力

| 名前 | 種類 | 説明 |
|------|------|------|
| lora_weight | STRING (ウィジェット + ソケット接続可) | ファイル名の `%LoraWeight%` と置換されるテキスト |

#### filename_prefix の変数展開

`filename_prefix` ウィジェットで使用できる変数:

| 変数 | 説明 | 例 |
|------|------|-----|
| `%LoraWeight%` | `lora_weight` 入力の値 | `add-detail-xl-0.30` |
| `%date:FORMAT%` | 日付（Java形式フォーマット） | `%date:yyyy-MM-dd%` → `2026-04-30` |
| `%date%` | 日時（`yyyyMMddhhmmss` 固定） | `20260430143000` |
| `%NodeType.widget%` | 任意ノードのウィジェット値 | `%KSampler.cfg%` → `5` |
| `%width%`, `%height%` | 画像サイズ（ComfyUI コア処理） | |
| `%year%`, `%month%`, `%day%` 等 | 個別日時要素（ComfyUI コア処理） | |

#### フロントエンドの変数展開に関する注意

ComfyUI フロントエンドの `Comfy.SaveImageExtraOutput` 拡張は既知ノード（`SaveImage`, `SaveVideo` 等）の `filename_prefix` ウィジェットにのみ `serializeValue` を追加し、`%NodeType.widget%` と `%date:FORMAT%` を置換する。カスタムノードはこの対象外のため、両方ともサーバー側（Python）で処理する必要がある。

- `%date:FORMAT%` → `_apply_date_vars()` で Python 側処理
- `%NodeType.widget%` → `_apply_node_vars(prompt)` で Python 側処理（hidden 入力 `PROMPT` を参照）
  - `prompt` 内の `class_type` でノードを検索し、ウィジェット値（プリミティブ）を取得
  - リンク接続値（`[node_id, slot]` 配列）は対象外

---

## カスタムノード API について

### 旧来の API（推奨）

テキスト表示など UI 絡みの機能は旧来の API が確実。

```python
class MyNode:
    CATEGORY = "text"
    OUTPUT_NODE = True          # ui 出力を使う場合は必須
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("出力名",)
    FUNCTION = "execute"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),       # ソケット接続専用
                "value": ("STRING", {"default": "", "multiline": False}),  # ウィジェット
            },
            "optional": {
                "opt": ("STRING", {"forceInput": True}),
            },
        }

    def execute(self, text, value, opt=""):
        # ui キーでフロントエンドに表示データを送信
        # result キーで出力ソケットの値を返す
        return {
            "ui": {"text": [display_text1, display_text2]},
            "result": (output_string,),
        }

NODE_CLASS_MAPPINGS = {"MyNode": MyNode}
NODE_DISPLAY_NAME_MAPPINGS = {"MyNode": "My Node"}
WEB_DIRECTORY = "./web/js"  # JS 拡張がある場合
```

### ノード上にテキストを表示する方法

`OUTPUT_NODE = True` + `{"ui": {"text": [...]}}` だけでは表示されない。
**JS 拡張が必須。**

```js
// web/js/myNode.js
import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

app.registerExtension({
    name: "custom.MyNode",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "MyNode") return;

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);
            // message.text に ui.text の配列が入る
            for (const text of message.text ?? []) {
                const w = ComfyWidgets["STRING"](this, "preview", ["STRING", { multiline: true }], app).widget;
                w.inputEl.readOnly = true;
                w.value = text;
            }
            requestAnimationFrame(() => {
                const sz = this.computeSize();
                this.onResize?.(sz);
                app.graph.setDirtyCanvas(true, false);
            });
        };
    },
});
```

### 実行後にウィジェット値を更新する方法

別途プレビューウィジェットを追加せず、既存ウィジェットに値を反映する場合:

```js
nodeType.prototype.onExecuted = function (message) {
    onExecuted?.apply(this, arguments);
    const textWidget = this.widgets?.find(w => w.name === "text");
    if (textWidget) {
        textWidget.value = message.text?.[0] ?? "";
    }
    requestAnimationFrame(() => { /* リサイズ処理 */ });
};
```

### 動的入力ソケット（入力数を可変にする）

Python 側では `**kwargs` で動的入力を受け取り、JS 側でソケットを追加・削除する。

```python
@classmethod
def INPUT_TYPES(cls):
    return {
        "required": {
            "input_count": ("INT", {"default": 4, "min": 1, "step": 1, "display": "number"}),
        },
    }

def execute(self, input_count, **kwargs):
    for i in range(1, input_count + 1):
        t = kwargs.get(f"text_{i}") or ""
```

```js
function syncInputs(node) {
    const count = node.widgets?.find(w => w.name === "input_count")?.value ?? 4;
    const current = (node.inputs ?? []).filter(inp => inp.name.startsWith("text_")).length;

    if (count > current) {
        for (let i = current + 1; i <= count; i++) node.addInput(`text_${i}`, "STRING");
    } else {
        for (let i = current; i > count; i--) {
            const idx = [...(node.inputs ?? [])].reverse().findIndex(inp => inp.name === `text_${i}`);
            if (idx !== -1) node.removeInput(node.inputs.length - 1 - idx);
        }
    }
    app.graph.setDirtyCanvas(true, false);
}

// onNodeCreated でボタン追加 + 新規ノードの初期化（configure 後に実行）
nodeType.prototype.onNodeCreated = function () {
    this.addWidget("button", "入力数を更新", null, () => syncInputs(this));
    const self = this;
    requestAnimationFrame(() => {
        if (!(self.inputs ?? []).some(inp => inp.name.startsWith("text_"))) {
            syncInputs(self);
        }
    });
};

// ロード時: 旧フォーマット入力の除去と再初期化
nodeType.prototype.onConfigure = function (data) {
    // 旧フォーマット (textN) を削除してから新フォーマット (text_N) に統一
};
```

**注意:** `requestAnimationFrame` で遅延させることで `configure()` の後に実行され、ロード時の二重追加を防げる。

### 既存ノードを継承する方法

`nodes` モジュールは ComfyUI 本体のモジュール。IDE では解決できないが実行時には利用可能。

```python
from nodes import SaveImage  # type: ignore[import]

class MySaveNode(SaveImage):
    FUNCTION = "my_save"

    @classmethod
    def INPUT_TYPES(cls):
        inputs = super().INPUT_TYPES()
        inputs["required"]["my_param"] = ("STRING", {"default": ""})
        return inputs

    def my_save(self, images, filename_prefix="ComfyUI", my_param="", prompt=None, extra_pnginfo=None):
        # 前処理
        return super().save_images(images=images, filename_prefix=filename_prefix, prompt=prompt, extra_pnginfo=extra_pnginfo)
```

### filename_prefix の変数展開をカスタムノードで行う

ComfyUI コア (`folder_paths.compute_vars`) が処理するのは `%width%`, `%height%`, `%year%`, `%month%`, `%day%`, `%hour%`, `%minute%`, `%second%` のみ。`%date:FORMAT%` と `%NodeType.widget%` はフロントエンド JS が既知ノードのみ処理するため、カスタムノードでは Python 側で実装が必要。

```python
import re, time

@staticmethod
def _apply_date_vars(prefix: str) -> str:
    now = time.localtime()
    def format_date(fmt: str) -> str:
        result = fmt
        result = result.replace("yyyy", f"{now.tm_year:04d}")
        result = result.replace("yy",   f"{now.tm_year % 100:02d}")
        result = result.replace("MM",   f"{now.tm_mon:02d}")   # 月（大文字）を先に
        result = result.replace("dd",   f"{now.tm_mday:02d}")
        result = result.replace("hh",   f"{now.tm_hour:02d}")
        result = result.replace("mm",   f"{now.tm_min:02d}")   # 分（小文字）を後に
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
        def replace_node_ref(m):
            for inputs in node_map.get(m.group(1), []):
                val = inputs.get(m.group(2))
                if val is not None and not isinstance(val, list):  # リンク値はスキップ
                    return str(val)
            return m.group(0)
        return re.sub(r'%([^%.]+)\.([^%]+)%', replace_node_ref, prefix)
    except Exception:
        return prefix
```

### 新しい API (`comfy_api.latest`)

テキスト表示ウィジェットには対応していないため、表示が必要なノードには旧来の API を使うこと。

```python
from comfy_api.latest import ComfyExtension, io, ui

class MyNode(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="MyNode",
            display_name="My Node",
            category="text",
            is_output_node=True,  # ui 出力を使う場合
            inputs=[
                io.String.Input("text", force_input=True),           # ソケット接続専用
                io.String.Input("value", multiline=False, default=""), # ウィジェット
            ],
            outputs=[io.String.Output(display_name="出力名")],
        )

    @classmethod
    def execute(cls, text, value) -> io.NodeOutput:
        return io.NodeOutput(result)

class MyExtension(ComfyExtension):
    async def get_node_list(self):
        return [MyNode]

async def comfy_entrypoint():
    return MyExtension()
```
