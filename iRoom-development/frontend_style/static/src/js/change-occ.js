function replaceOdooInNode(node) {
    if (node.nodeType === 3) {
        node.nodeValue = node.nodeValue.replace(/odoo|Odoo|أودو|اودو/g, "iroom");
    } else {
        node.childNodes.forEach(replaceOdooInNode);
    }
}

(function () {
    function swapIcon(el) {
        if (!el || !el.classList) return;
        if (el.classList.contains('ri-apps-2-line')) {
            el.classList.remove('ri-apps-2-line');
            el.classList.add('ri-home-3-line');
        } else if (el.classList.contains('ri-apps-2-fill')) {
            el.classList.remove('ri-apps-2-fill');
            el.classList.add('ri-home-3-line');
        }
    }

    function scan(root) {
        if (!root || !root.querySelectorAll) {
            swapIcon(root);
            return;
        }
        root.querySelectorAll('.ri-apps-2-line, .ri-apps-2-fill').forEach(swapIcon);
        swapIcon(root);
    }

    document.addEventListener('DOMContentLoaded', function () {
        replaceOdooInNode(document.body);

        scan(document.body);

        const observer = new MutationObserver((muts) => {
            for (const m of muts) {
                if (m.type === 'childList') {
                    m.addedNodes.forEach((n) => {
                        replaceOdooInNode(n);
                        scan(n);
                    });
                } else if (m.type === 'attributes' && m.attributeName === 'class') {
                    swapIcon(m.target);
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class']
        });

        setTimeout(() => scan(document.body), 300);
        setTimeout(() => scan(document.body), 1500);
        setTimeout(() => scan(document.body), 4000);
    });
})();