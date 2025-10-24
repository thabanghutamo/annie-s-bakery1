// Cart management using localStorage
const CART_KEY = 'annies_cart';

class Cart {
    constructor() {
        // Set initial state
        this.updateAuthState();
    }

    // Helper function to format price consistently
    formatPrice(price) {
        return parseFloat(price).toFixed(2);
    }

    updateAuthState() {
        const wasAuthorized = this.authorized;
        this.authorized = window.isAuthenticated || false;
        
        // Only load items from storage if newly authorized
        if (!wasAuthorized && this.authorized) {
            this.items = this.load();
        } else if (!this.authorized) {
            this.items = [];
        }
        
        this.updateUI();
    }

    load() {
        const stored = localStorage.getItem(CART_KEY);
        return stored ? JSON.parse(stored) : [];
    }

    save() {
        if (this.authorized) {
            localStorage.setItem(CART_KEY, JSON.stringify(this.items));
            this.updateUI();
        }
    }

    add(id, title, price, image) {
        if (!this.authorized) {
            window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
            return;
        }
        
        const existing = this.items.find(i => i.id === id);
        if (existing) {
            existing.quantity = (existing.quantity || 1) + 1;
        } else {
            this.items.push({
                id: id,
                title: title,
                price: price,
                image: image,
                quantity: 1
            });
        }
        this.save();
        this.showNotification('Added to cart');
    }

    remove(productId) {
        if (!this.authorized) return;
        
        this.items = this.items.filter(i => i.id !== productId);
        this.save();
    }

    updateQuantity(productId, qty) {
        if (!this.authorized) return;

        const item = this.items.find(i => i.id === productId);
        if (item) {
            item.quantity = Math.max(1, parseInt(qty) || 1);
            this.save();
        }
    }

    clear() {
        if (!this.authorized) return;
        
        this.items = [];
        this.save();
    }

    getTotal() {
        return this.items.reduce((sum, item) => 
            sum + (parseFloat(item.price) * (item.quantity || 1)), 0);
    }

    updateUI() {
        // Update cart count in header
        const count = this.authorized ? this.items.reduce((sum, item) => sum + (item.quantity || 1), 0) : 0;
        document.querySelectorAll('.cart-count').forEach(el => {
            el.textContent = count;
        });

        // Update cart page if it exists
        const cartTable = document.querySelector('#cart-items');
        const cartContainer = document.querySelector('#cart-items')?.closest('.bg-white');
        const emptyMessage = document.querySelector('#empty-cart');
        
        if (cartTable) {
            if (!this.authorized) {
                if (cartContainer) cartContainer.style.display = 'none';
                if (emptyMessage) {
                    emptyMessage.style.display = 'block';
                    const title = emptyMessage.querySelector('h3');
                    const desc = emptyMessage.querySelector('p');
                    if (title) title.textContent = 'Please sign in to view your cart';
                    if (desc) desc.textContent = 'Sign in to see your cart items and complete your purchase.';
                }
                return;
            }

            if (this.items.length === 0) {
                if (cartContainer) cartContainer.style.display = 'none';
                if (emptyMessage) {
                    emptyMessage.style.display = 'block';
                    const title = emptyMessage.querySelector('h3');
                    const desc = emptyMessage.querySelector('p');
                    if (title) title.textContent = 'Your cart is empty';
                    if (desc) desc.textContent = 'Add some delicious items to get started!';
                }
                return;
            }

            // Show cart table and hide empty message
            if (cartContainer) cartContainer.style.display = 'block';
            if (emptyMessage) emptyMessage.style.display = 'none';

            // Update cart items
            cartTable.innerHTML = this.items.map(item => `
                <tr>
                    <td class="px-6 py-4">${item.title}</td>
                    <td class="px-6 py-4 text-right">R${this.formatPrice(item.price)}</td>
                    <td class="px-6 py-4 text-right">
                        <input type="number" min="1" value="${item.quantity || 1}"
                            class="w-20 text-right border-gray-300 rounded-md shadow-sm focus:ring-pink-500 focus:border-pink-500"
                            onchange="cart.updateQuantity('${item.id}', this.value)">
                    </td>
                    <td class="px-6 py-4 text-right">R${this.formatPrice(item.price * (item.quantity || 1))}</td>
                    <td class="px-6 py-4 text-right">
                        <button onclick="cart.remove('${item.id}')" 
                                class="text-red-600 hover:text-red-700">Remove</button>
                    </td>
                </tr>
            `).join('');
        }

        // Update total with R prefix and proper decimal formatting
        const totalEl = document.querySelector('#cart-total');
        if (totalEl) {
            totalEl.textContent = this.formatPrice(this.getTotal());
        }

        // Dispatch event for cart update
        document.dispatchEvent(new CustomEvent('cartUpdated'));
    }

    showNotification(message) {
        const div = document.createElement('div');
        div.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow';
        div.textContent = message;
        document.body.appendChild(div);
        setTimeout(() => div.remove(), 3000);
    }

    async checkout() {
        if (!this.authorized) {
            window.location.href = `/login?next=${encodeURIComponent('/cart')}`;
            return;
        }

        if (this.items.length === 0) {
            alert('Your cart is empty');
            return;
        }

        try {
            const response = await fetch('/cart/checkout', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    items: this.items,
                    total: this.getTotal()
                })
            });
            
            const result = await response.json();
            if (result.success) {
                window.location.href = result.checkoutUrl;
            } else {
                alert(result.error || 'Checkout failed');
            }
        } catch (err) {
            console.error('Checkout error:', err);
            alert('Could not process checkout');
        }
    }
}

// Initialize cart
const cart = new Cart();
document.addEventListener('DOMContentLoaded', () => {
    // Set cart authorization status (will be set in the template)
    cart.updateUI();
});
