// Initialize Supabase Client
const supabaseUrl = 'https://yqvjqdontrnqdvmqdbtl.supabase.co';
const supabaseKey = 'sb_publishable_CS1yiPqr6vSeRQ-3YIGwHQ_0nbRlC3R';
const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

const host = 'https://shopping-system-fast-api.onrender.com';

// Auth Elements
const authButtons = document.getElementById('auth-buttons');
const userProfile = document.getElementById('user-profile');
const userEmailSpan = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');

const openLoginBtn = document.getElementById('open-login-btn');
const openRegisterBtn = document.getElementById('open-register-btn');

// Modal Elements
const authModal = document.getElementById('auth-modal');
const modalClose = document.getElementById('modal-close');
const modalTitle = document.getElementById('modal-title');
const modalEmailInput = document.getElementById('modal-email');
const modalPasswordInput = document.getElementById('modal-password');
const modalSubmitBtn = document.getElementById('modal-submit-btn');
const modalToggleText = document.getElementById('modal-toggle-text');

// Cart Elements
const cartPanel = document.getElementById('cart-panel');
const cartOverlay = document.getElementById('cart-overlay');
const cartToggleBtn = document.getElementById('cart-toggle-btn');
const cartCloseBtn = document.getElementById('cart-close-btn');
const cartItemsContainer = document.getElementById('cart-items');
const cartCountSpan = document.getElementById('cart-count');
const cartTotalAmountSpan = document.getElementById('cart-total-amount');

// Auth State
let currentUser = null;
let modalMode = 'login'; // 'login' or 'register'
let cartItems = [];

// Modal Logic
function openModal(mode = 'login') {
    modalMode = mode;
    updateModalUI();
    authModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    authModal.style.display = 'none';
    document.body.style.overflow = 'auto';
    modalEmailInput.value = '';
    modalPasswordInput.value = '';
}

function updateModalUI() {
    if (modalMode === 'login') {
        modalTitle.textContent = 'Login';
        modalSubmitBtn.textContent = 'Login';
        modalToggleText.innerHTML = `Don't have an account? <a href="#" id="modal-toggle-link">Register</a>`;
    } else {
        modalTitle.textContent = 'Register';
        modalSubmitBtn.textContent = 'Create Account';
        modalToggleText.innerHTML = `Already have an account? <a href="#" id="modal-toggle-link">Login</a>`;
    }

    // Add click event for toggle link
    const toggleLink = document.getElementById('modal-toggle-link');
    if (toggleLink) {
        toggleLink.onclick = (e) => {
            e.preventDefault();
            modalMode = (modalMode === 'login') ? 'register' : 'login';
            updateModalUI();
        };
    }
}

// Auth Functions
async function handleAuthAction() {
    const email = modalEmailInput.value;
    const password = modalPasswordInput.value;
    if (!email || !password) return alert('Please enter email and password');

    if (modalMode === 'login') {
        const { data, error } = await supabaseClient.auth.signInWithPassword({ email, password });
        if (error) alert(error.message);
        else closeModal();
    } else {
        const { data, error } = await supabaseClient.auth.signUp({ email, password });
        if (error) {
            alert(error.message);
        } else {
            alert('Registration successful! Please check your email.');
            modalMode = 'login';
            updateModalUI();
        }
    }
}

async function handleLogout() {
    const { error } = await supabaseClient.auth.signOut();
    if (error) alert(error.message);
}

function updateAuthState(user) {
    currentUser = user;
    if (user) {
        if (authButtons) authButtons.style.display = 'none';
        if (userProfile) userProfile.style.display = 'flex';
        userEmailSpan.textContent = user.email;
    } else {
        if (authButtons) authButtons.style.display = 'flex';
        if (userProfile) userProfile.style.display = 'none';
        userEmailSpan.textContent = '';
    }
    fetchProducts();
    if (user) {
        fetchCart();
    } else {
        cartItems = [];
        updateCartUI();
    }
}

// Cart Logic
function toggleCart(show) {
    if (show) {
        cartPanel.classList.add('open');
        cartOverlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    } else {
        cartPanel.classList.remove('open');
        cartOverlay.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

async function fetchCart() {
    try {
        const { data, error } = await supabaseClient
            .from('cart_items')
            .select(`
                id,
                product_id,
                quantity,
                products (
                    name,
                    price
                )
            `);

        if (error) throw error;
        cartItems = data || [];
        updateCartUI();
    } catch (error) {
        console.error('Error fetching cart:', error);
    }
}

async function addToCart(productId) {
    if (!currentUser) return openModal('login');

    try {
        const { data: { session } } = await supabaseClient.auth.getSession();
        const token = session?.access_token;

        const response = await fetch(`${host}/cart/add-item`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        if (!response.ok) throw new Error('Failed to add item to cart');

        fetchCart();
    } catch (error) {
        console.error('Error adding to cart:', error);
        alert('Error adding to cart');
    }
}

async function removeFromCart(productId, quantity = 1) {
    try {
        const { data: { session } } = await supabaseClient.auth.getSession();
        const token = session?.access_token;

        const response = await fetch(`${host}/cart/remove-item`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });

        if (!response.ok) throw new Error('Failed to remove item from cart');

        fetchCart();
    } catch (error) {
        console.error('Error removing from cart:', error);
        alert('Error removing from cart');
    }
}

function updateCartUI() {
    // Update count
    const totalItems = cartItems.reduce((acc, item) => acc + item.quantity, 0);
    if (cartCountSpan) cartCountSpan.textContent = totalItems;

    // Render items
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = '';
        let totalAmount = 0;

        if (cartItems.length === 0) {
            cartItemsContainer.innerHTML = '<p style="color: var(--text-secondary); text-align: center; margin-top: 2rem;">Your cart is empty.</p>';
        } else {
            cartItems.forEach(item => {
                const itemTotal = item.products.price * item.quantity;
                totalAmount += itemTotal;

                const itemElement = document.createElement('div');
                itemElement.className = 'cart-item';
                itemElement.innerHTML = `
                    <div class="cart-item-details">
                        <div class="cart-item-name">${item.products.name}</div>
                        <div class="cart-item-price">${formatCurrency(item.products.price)}</div>
                        <div class="cart-item-quantity">
                            <button class="quantity-btn" onclick="removeFromCart(${item.product_id}, 1)">-</button>
                            <span>${item.quantity}</span>
                            <button class="quantity-btn" onclick="addToCart(${item.product_id})">+</button>
                        </div>
                    </div>
                    <div class="cart-item-total" style="font-weight: 600;">
                        ${formatCurrency(itemTotal)}
                    </div>
                `;
                cartItemsContainer.appendChild(itemElement);
            });
        }
        if (cartTotalAmountSpan) cartTotalAmountSpan.textContent = formatCurrency(totalAmount);
    }
}

// Event Listeners
openLoginBtn.addEventListener('click', () => openModal('login'));
openRegisterBtn.addEventListener('click', () => openModal('register'));
modalClose.addEventListener('click', closeModal);
authModal.addEventListener('click', (e) => {
    if (e.target === authModal) closeModal();
});
modalSubmitBtn.addEventListener('click', handleAuthAction);
logoutBtn.addEventListener('click', handleLogout);
if (cartToggleBtn) cartToggleBtn.addEventListener('click', () => toggleCart(true));
if (cartCloseBtn) cartCloseBtn.addEventListener('click', () => toggleCart(false));
if (cartOverlay) cartOverlay.addEventListener('click', () => toggleCart(false));

// Enter key support
[modalEmailInput, modalPasswordInput].forEach(input => {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleAuthAction();
    });
});

// Listen to auth state changes
supabaseClient.auth.onAuthStateChange((event, session) => {
    updateAuthState(session?.user ?? null);
});

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function enableEditMode(productId, currentName) {
    const titleElement = document.getElementById(`title-${productId}`);
    const actionsElement = document.getElementById(`actions-${productId}`);

    // Replace title with input
    titleElement.innerHTML = `
        <input type="text" id="input-${productId}" value="${currentName}" class="edit-input" />
    `;

    // Replace Edit button with Save/Cancel
    actionsElement.innerHTML = `
        <button onclick="saveProduct(${productId})" class="btn-save">Save</button>
        <button onclick="cancelEditMode(${productId}, '${currentName}')" class="btn-cancel">Cancel</button>
    `;
}

function cancelEditMode(productId, originalName) {
    const titleElement = document.getElementById(`title-${productId}`);
    const actionsElement = document.getElementById(`actions-${productId}`);

    titleElement.textContent = originalName;
    actionsElement.innerHTML = `
        <button onclick="enableEditMode(${productId}, '${originalName}')" class="btn-edit">Edit</button>
    `;
}

async function saveProduct(productId) {
    const inputElement = document.getElementById(`input-${productId}`);
    const newName = inputElement.value;

    if (!newName) return alert('Name cannot be empty');

    try {
        const { data: { session } } = await supabaseClient.auth.getSession();
        const token = session?.access_token;

        if (!token) return alert('You must be logged in to edit.');

        const response = await fetch(`${host}/products/${productId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name: newName })
        });

        if (!response.ok) {
            throw new Error('Failed to update product');
        }

        // Refresh products
        fetchProducts();

    } catch (error) {
        console.error('Error updating product:', error);
        alert('Error updating product: ' + error.message);
    }
}

function renderProducts(products) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = '';

    if (products.length === 0) {
        grid.innerHTML = '<p class="no-products">No products found.</p>';
        return;
    }

    products.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';

        // Stock logic for visual feedback
        const isLowStock = product.stock < 50;
        const stockClass = isLowStock ? 'stock-low' : 'stock-high';

        const editButton = currentUser
            ? `<div id="actions-${product.product_id}" class="card-actions">
                 <button onclick="enableEditMode(${product.product_id}, '${product.name.replace(/'/g, "\\'")}')" class="btn-edit">Edit</button>
               </div>`
            : '';

        card.innerHTML = `
            <div class="card-header">
                <span class="category-badge">${product.category_name || 'Uncategorized'}</span>
                ${editButton}
            </div>
            <h2 id="title-${product.product_id}" class="product-name">${product.name}</h2>
            <p class="product-description">${product.description || ''}</p>
            <div class="card-footer">
                <div class="product-price">${formatCurrency(product.price)}</div>
                <div class="product-stock ${stockClass}">
                    ${product.stock} in stock
                </div>
            </div>
            <div style="margin-top: 1rem; display: flex; justify-content: flex-end;">
                <button onclick="addToCart(${product.product_id})" class="btn-add-cart">
                    Add to Cart
                </button>
            </div>
        `;

        grid.appendChild(card);
    });
}

function showError(message) {
    const grid = document.getElementById('product-grid');
    grid.innerHTML = `
        <div class="error-message" style="color: #f87171; text-align: center; grid-column: 1/-1;">
            <h3>Error Loading Products</h3>
            <p>${message}</p>
            <p style="font-size: 0.8rem; margin-top: 1rem; color: #94a3b8;">
                Make sure you have replaced YOUR_SUPABASE_URL and YOUR_SUPABASE_ANON_KEY in app.js
            </p>
        </div>
    `;
}

async function fetchProducts() {
    const grid = document.getElementById('product-grid');
    // Only show loading if empty, to avoid flickering on re-fetch
    if (!grid.hasChildNodes()) {
        grid.innerHTML = '<p style="color: var(--text-secondary); text-align: center; grid-column: 1/-1;">Loading products...</p>';
    }

    try {
        const { data, error } = await supabaseClient
            .from('products_view')
            .select('*')
            .order('product_id', { ascending: true }); // Ensure stable order

        if (error) {
            throw error;
        }

        renderProducts(data);
    } catch (error) {
        console.error('Error fetching products:', error);
        showError(error.message);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check initial session
    supabaseClient.auth.getSession().then(({ data: { session } }) => {
        updateAuthState(session?.user ?? null);
    });
});
