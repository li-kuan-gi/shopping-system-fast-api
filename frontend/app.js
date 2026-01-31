// Initialize Supabase Client
const supabaseUrl = 'https://yqvjqdontrnqdvmqdbtl.supabase.co';
const supabaseKey = 'sb_publishable_CS1yiPqr6vSeRQ-3YIGwHQ_0nbRlC3R';
const supabaseClient = supabase.createClient(supabaseUrl, supabaseKey);

// Auth Elements
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const registerBtn = document.getElementById('register-btn');
const logoutBtn = document.getElementById('logout-btn');
const authForms = document.getElementById('auth-forms');
const userProfile = document.getElementById('user-profile');
const userEmailSpan = document.getElementById('user-email');

// Auth Functions
let currentUser = null;

async function handleLogin() {
    const email = emailInput.value;
    const password = passwordInput.value;
    if (!email || !password) return alert('Please enter email and password');

    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
    });

    if (error) alert(error.message);
}

async function handleRegister() {
    const email = emailInput.value;
    const password = passwordInput.value;
    if (!email || !password) return alert('Please enter email and password');

    const { data, error } = await supabaseClient.auth.signUp({
        email,
        password
    });

    if (error) {
        alert(error.message);
    } else {
        alert('Registration successful! Please check your email/login.');
    }
}

async function handleLogout() {
    const { error } = await supabaseClient.auth.signOut();
    if (error) alert(error.message);
}

function updateAuthState(user) {
    currentUser = user; // Store globally
    if (user) {
        authForms.style.display = 'none';
        userProfile.style.display = 'flex';
        userEmailSpan.textContent = user.email;
    } else {
        authForms.style.display = 'flex';
        userProfile.style.display = 'none';
        userEmailSpan.textContent = '';
        emailInput.value = '';
        passwordInput.value = '';
    }
    // Re-fetch products to update UI (show/hide edit buttons)
    fetchProducts();
}

// Event Listeners
loginBtn.addEventListener('click', handleLogin);
registerBtn.addEventListener('click', handleRegister);
logoutBtn.addEventListener('click', handleLogout);

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

        const response = await fetch(`http://localhost:8000/products/${productId}`, {
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
