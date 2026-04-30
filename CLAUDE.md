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
