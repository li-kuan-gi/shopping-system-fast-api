// Initialize Supabase Client
const supabaseUrl = 'https://yqvjqdontrnqdvmqdbtl.supabase.co';
const supabaseKey = 'sb_publishable_CS1yiPqr6vSeRQ-3YIGwHQ_0nbRlC3R';
const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

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

// Auth State
let currentUser = null;
let modalMode = 'login'; // 'login' or 'register'

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

        const response = await fetch(`https://clean-vilma-explore-new-worlds-f9495307.koyeb.app/products/${productId}`, {
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
