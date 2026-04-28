import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

const NODE_NAME = "RegexReplaceNode";
const INPUT_PREFIX = "text_";
const INPUT_TYPE = "STRING";
const DEFAULT_COUNT = 4;

// 旧フォーマット (text1, text2, ...) にマッチする正規表現
const OLD_INPUT_RE = /^text\d+$/;

/** input_count ウィジェットの値を取得 */
function getInputCount(node) {
    return node.widgets?.find(w => w.name === "input_count")?.value ?? DEFAULT_COUNT;
}

/** text_N 入力ソケットを count 個に合わせて追加・削除 */
function syncInputs(node) {
    const count = getInputCount(node);
    const textInputs = (node.inputs ?? []).filter(inp => inp.name.startsWith(INPUT_PREFIX));
    const current = textInputs.length;

    if (count > current) {
        for (let i = current + 1; i <= count; i++) {
            node.addInput(`${INPUT_PREFIX}${i}`, INPUT_TYPE);
        }
    } else if (count < current) {
        for (let i = current; i > count; i--) {
            let idx = -1;
            for (let j = node.inputs.length - 1; j >= 0; j--) {
                if (node.inputs[j].name === `${INPUT_PREFIX}${i}`) {
                    idx = j;
                    break;
                }
            }
            if (idx !== -1) node.removeInput(idx);
        }
    }

    app.graph.setDirtyCanvas(true, false);
}

/** 旧フォーマット (text1〜text5) の入力ソケットを削除 */
function removeOldInputs(node) {
    if (!node.inputs) return;
    for (let i = node.inputs.length - 1; i >= 0; i--) {
        if (OLD_INPUT_RE.test(node.inputs[i].name)) {
            node.removeInput(i);
        }
    }
}

app.registerExtension({
    name: `custom.${NODE_NAME}`,
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_NAME) return;

        /** ノード作成時: ボタンを追加し、新規ノードの初期入力を遅延追加 */
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            this.addWidget("button", "Update num of inputs / 入力数を更新", null, () => {
                syncInputs(this);
            });

            // requestAnimationFrame で configure() の後に実行されることを保証する。
            // ロード時は configure() が入力を復元するため syncInputs をスキップする。
            const self = this;
            requestAnimationFrame(() => {
                // 新規ノード: text_ 入力がまだ存在しない場合のみ初期化
                const hasNew = (self.inputs ?? []).some(inp => inp.name.startsWith(INPUT_PREFIX));
                if (!hasNew) {
                    syncInputs(self);
                }
            });
        };

        /** ロード時: 旧フォーマット入力を除去して新フォーマットに統一 */
        const onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (data) {
            onConfigure?.apply(this, arguments);

            // 旧フォーマット (text1〜textN) が残っていれば削除
            removeOldInputs(this);

            // 旧フォーマットを削除した結果、text_ 入力がゼロになった場合は再初期化
            const hasNew = (this.inputs ?? []).some(inp => inp.name.startsWith(INPUT_PREFIX));
            if (!hasNew) {
                syncInputs(this);
            }
        };

        /** 実行後: マージ後・置換後テキストをノード上に表示 */
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            // 既存プレビューウィジェットを削除
            if (this.widgets) {
                const toRemove = this.widgets.filter(w => w._isPreview);
                for (const w of toRemove) {
                    w.onRemove?.();
                    this.widgets.splice(this.widgets.indexOf(w), 1);
                }
            }

            const labels = ["merged text / マージ後テキスト", "replaced text / 置換後テキスト"];
            for (let i = 0; i < (message.text?.length ?? 0); i++) {
                const w = ComfyWidgets["STRING"](
                    this,
                    labels[i] ?? `preview_${i}`,
                    ["STRING", { multiline: true }],
                    app
                ).widget;
                w.inputEl.readOnly = true;
                w.inputEl.style.opacity = 0.6;
                w.value = message.text[i] ?? "";
                w._isPreview = true;
            }

            requestAnimationFrame(() => {
                const sz = this.computeSize();
                if (sz[0] < this.size[0]) sz[0] = this.size[0];
                if (sz[1] < this.size[1]) sz[1] = this.size[1];
                this.onResize?.(sz);
                app.graph.setDirtyCanvas(true, false);
            });
        };
    },
});
