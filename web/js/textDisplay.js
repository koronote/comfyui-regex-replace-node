import { app } from "../../../scripts/app.js";

const NODE_NAME = "TextDisplayNode";

app.registerExtension({
    name: `custom.${NODE_NAME}`,
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_NAME) return;

        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            onExecuted?.apply(this, arguments);

            const text = message.text?.[0] ?? "";
            const textWidget = this.widgets?.find(w => w.name === "text");
            if (textWidget) {
                textWidget.value = text;
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
