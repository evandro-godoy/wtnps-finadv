/* virtual-scroll.js - lightweight virtual list helper */

class VirtualScroll {
    constructor(container, options = {}) {
        this.container = container;
        this.rowHeight = options.rowHeight || 56;
        this.renderRow = options.renderRow || (() => document.createElement('div'));
        this.items = [];

        this.container.classList.add('virtual-scroll');
        this.container.innerHTML = '';

        this.spacer = document.createElement('div');
        this.spacer.className = 'virtual-scroll-spacer';

        this.inner = document.createElement('div');
        this.inner.className = 'virtual-scroll-inner';

        this.container.appendChild(this.spacer);
        this.container.appendChild(this.inner);

        this.container.addEventListener('scroll', () => this.render());
    }

    setItems(items) {
        this.items = items || [];
        this.spacer.style.height = `${this.items.length * this.rowHeight}px`;
        this.render();
    }

    render() {
        const scrollTop = this.container.scrollTop;
        const viewportHeight = this.container.clientHeight;
        const startIndex = Math.max(0, Math.floor(scrollTop / this.rowHeight) - 2);
        const endIndex = Math.min(
            this.items.length,
            Math.ceil((scrollTop + viewportHeight) / this.rowHeight) + 2
        );

        this.inner.innerHTML = '';

        for (let i = startIndex; i < endIndex; i += 1) {
            const row = this.renderRow(this.items[i], i);
            row.style.position = 'absolute';
            row.style.top = `${i * this.rowHeight}px`;
            row.style.left = '0';
            row.style.right = '0';
            this.inner.appendChild(row);
        }
    }
}

class PredictionVirtualScroll extends VirtualScroll {
    constructor(container, options = {}) {
        super(container, {
            rowHeight: options.rowHeight || 64,
            renderRow: (item) => {
                const row = document.createElement('div');
                row.className = `signal-history-item ${item.ai_signal.toLowerCase()}`;

                const time = document.createElement('div');
                time.className = 'signal-history-time';
                time.textContent = formatTime(new Date(item.timestamp));

                const content = document.createElement('div');
                content.className = 'signal-history-content';
                content.innerHTML = `
                    <div><strong>${item.ai_signal}</strong> @ ${item.price.toFixed(2)}</div>
                    <div>${(item.probability * 100).toFixed(1)}% | ${item.indicators?.trend || '-'}</div>
                `;

                row.appendChild(time);
                row.appendChild(content);
                return row;
            }
        });
    }
}
