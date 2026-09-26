<!DOCTYPE html>
<html lang="en" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANUAARI MATERIALS | Aari & Craft Supplies</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    colors: {
                        plum: {
                            DEFAULT: '#6b1d4f',
                            dark: '#53143c',
                            light: '#8a2b64',
                            surface: '#faf7f9',
                            border: '#f3e8f1'
                        },
                        gold: '#d97706'
                    }
                }
            }
        }
    </script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #faf7f9;
            color: #2d1524;
        }
        .custom-scrollbar::-webkit-scrollbar {
            height: 6px;
            width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }
        .product-card {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .product-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 25px rgba(107, 29, 79, 0.1) !important;
            border-color: #e8d0e4 !important;
        }
    </style>
</head>
<body class="h-full flex flex-col antialiased">

    <div id="app" class="flex-1 flex flex-col min-h-screen">
        
        <!-- Login Screen Overlay -->
        <div id="loginModal" class="fixed inset-0 z-50 bg-plum/20 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl border border-plum-border shadow-2xl w-full max-w-md p-8 transform transition-all">
                <div class="text-center mb-6">
                    <div class="inline-block bg-plum/10 text-plum px-3 py-1 rounded-full text-xs font-extrabold uppercase tracking-widest mb-3">
                        Exclusive Store
                    </div>
                    <h1 class="text-2xl font-black text-plum tracking-tight uppercase">ANUAARI MATERIALS</h1>
                    <p class="text-xs font-bold text-gold italic lowercase mt-1">aari work supplies</p>
                </div>
                
                <div class="bg-plum-surface p-4 rounded-xl border border-plum-border mb-6 text-center">
                    <h2 class="text-base font-bold text-gray-900">Customer Sign In</h2>
                    <p class="text-xs text-gray-600 mt-0.5">Enter your name and mobile number to browse inventory</p>
                </div>

                <form id="loginForm" onsubmit="handleLogin(event)" class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Customer Name</label>
                        <input type="text" id="custName" required placeholder="e.g. Anusha" 
                            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-plum text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-gray-700 uppercase mb-1">10-Digit Mobile Number</label>
                        <input type="tel" id="custPhone" required maxlength="10" placeholder="9840450113" 
                            class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-plum text-sm">
                    </div>
                    <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-plum to-plum-dark text-white font-bold rounded-xl shadow-lg shadow-plum/20 hover:opacity-95 transition text-sm uppercase tracking-wider">
                        Enter Store
                    </button>
                </form>
            </div>
        </div>

        <!-- Main Storefront App View -->
        <div id="storeView" class="hidden flex-1 flex flex-col">
            
            <!-- Header Navigation -->
            <header class="bg-white border-b border-plum-border sticky top-0 z-30 px-4 lg:px-8 py-3.5 shadow-xs">
                <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
                    <div class="flex items-center gap-3">
                        <div class="bg-plum-surface px-4 py-2 rounded-xl border border-plum-border">
                            <span class="text-lg font-black text-plum uppercase tracking-wide">ANUAARI MATERIALS</span>
                            <span class="text-xs font-bold text-gold italic ml-2">aari supplies</span>
                        </div>
                    </div>

                    <div class="flex items-center gap-2 sm:gap-3">
                        <button onclick="switchView('Home')" id="navHomeBtn" class="px-4 py-2 rounded-xl text-sm font-bold bg-plum text-white transition shadow-sm">
                            <i class="fa-solid fa-store mr-1.5"></i> Home
                        </button>
                        <button onclick="switchView('Cart')" id="navCartBtn" class="px-4 py-2 rounded-xl text-sm font-bold bg-plum-surface text-plum border border-plum-border hover:bg-plum/10 transition relative">
                            <i class="fa-solid fa-cart-shopping mr-1.5"></i> Cart <span id="cartBadge" class="ml-1 bg-gold text-white text-xs px-2 py-0.5 rounded-full">0</span>
                        </button>
                        <button onclick="handleLogout()" class="px-3 py-2 rounded-xl text-sm font-bold text-red-600 hover:bg-red-50 transition border border-red-200">
                            <i class="fa-solid fa-right-from-bracket"></i>
                        </button>
                    </div>
                </div>
            </header>

            <!-- Main Content Area -->
            <main class="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6">
                
                <!-- HOME CATALOG VIEW -->
                <div id="homeSection" class="space-y-6">
                    <!-- Category Tabs -->
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-xs font-black uppercase text-plum tracking-wider flex items-center gap-1.5">
                                <i class="fa-solid fa-folder-open text-gold"></i> Master Categories
                            </h3>
                            <span id="welcomeUserDisplay" class="text-xs font-semibold text-gray-500"></span>
                        </div>
                        <div id="categoryContainer" class="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
                            <!-- Dynamically injected categories -->
                        </div>
                    </div>

                    <hr class="border-plum-border">

                    <!-- Product Grid Header -->
                    <div class="flex items-center justify-between">
                        <h2 id="currentCategoryTitle" class="text-lg font-black text-gray-900">All Products</h2>
                        <span id="productCountBadge" class="text-xs font-bold bg-plum/10 text-plum px-3 py-1 rounded-full">0 items</span>
                    </div>

                    <!-- Products Grid -->
                    <div id="productGrid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                        <!-- Dynamically injected products -->
                    </div>
                </div>

                <!-- CART & CHECKOUT VIEW -->
                <div id="cartSection" class="hidden space-y-6 max-w-3xl mx-auto">
                    <div class="bg-white p-6 rounded-2xl border border-plum-border shadow-xs">
                        <h2 class="text-xl font-black text-gray-900 mb-4 flex items-center gap-2">
                            <i class="fa-solid fa-cart-shopping text-plum"></i> Shopping Cart & Secure Checkout
                        </h2>
                        
                        <div id="cartItemsList" class="divide-y divide-gray-100 mb-6">
                            <!-- Cart items populated dynamically -->
                        </div>

                        <div id="emptyCartState" class="text-center py-12 hidden">
                            <div class="w-16 h-16 bg-plum-surface text-plum rounded-full flex items-center justify-center mx-auto mb-3 text-2xl">
                                <i class="fa-solid fa-basket-shopping"></i>
                            </div>
                            <p class="text-gray-600 font-semibold">Your cart is empty.</p>
                            <button onclick="switchView('Home')" class="mt-4 px-6 py-2.5 bg-plum text-white font-bold rounded-xl text-sm">
                                Browse Store Products
                            </button>
                        </div>

                        <div id="checkoutFormWrapper" class="hidden border-t border-plum-border pt-6">
                            <form onsubmit="handleCheckout(event)" class="space-y-4">
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Delivery Address (with Pincode):</label>
                                    <textarea id="checkoutAddress" required rows="3" placeholder="Door No, Street, City, State - Pincode"
                                        class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-plum text-sm"></textarea>
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Alternative Contact Number:</label>
                                    <input type="tel" id="checkoutSecPhone" required maxlength="10" placeholder="10-digit mobile number"
                                        class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-plum text-sm">
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Select Payment Method:</label>
                                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                        <label class="flex items-center gap-3 p-3 rounded-xl border border-gray-200 cursor-pointer hover:bg-plum-surface transition">
                                            <input type="radio" name="paymentMethod" value="Cash on Delivery (COD)" checked class="text-plum focus:ring-plum">
                                            <span class="text-sm font-bold text-gray-800">Cash on Delivery (COD)</span>
                                        </label>
                                        <label class="flex items-center gap-3 p-3 rounded-xl border border-gray-200 cursor-pointer hover:bg-plum-surface transition">
                                            <input type="radio" name="paymentMethod" value="Prepaid (GPay / PhonePe / UPI)" class="text-plum focus:ring-plum">
                                            <span class="text-sm font-bold text-gray-800">Prepaid (UPI / Cards)</span>
                                        </label>
                                    </div>
                                </div>
                                <div>
                                    <label class="block text-xs font-bold text-gray-700 uppercase mb-1">Custom Instructions / Notes:</label>
                                    <input type="text" id="checkoutNotes" placeholder="Any special requests or delivery notes"
                                        class="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-plum text-sm">
                                </div>
                                <button type="submit" class="w-full py-4 bg-gradient-to-r from-plum to-plum-dark text-white font-bold rounded-xl shadow-lg shadow-plum/20 hover:opacity-95 transition uppercase tracking-wider text-sm">
                                    Complete Order Now
                                </button>
                            </form>
                        </div>
                    </div>
                </div>

            </main>

            <!-- Footer -->
            <footer class="bg-white border-t border-plum-border py-4 px-6 text-center text-xs text-gray-500">
                &copy; 2026 ANUAARI MATERIALS. All rights reserved. Handcrafted with precision for Aari artisans.
            </footer>
        </div>
    </div>

    <!-- Toast Notification Modal/Alert Box -->
    <div id="toastNotification" class="fixed bottom-5 right-5 z-50 transform translate-y-20 opacity-0 transition-all duration-300 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-xl flex items-center gap-3 text-sm font-bold">
        <i class="fa-solid fa-circle-check text-green-400 text-lg"></i>
        <span id="toastMessage">Success message</span>
    </div>

    <script>
        const GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec";
        
        // Application State
        let state = {
            user: localStorage.getItem('anuaari_user') || null,
            phone: localStorage.getItem('anuaari_phone') || null,
            currentView: 'Home',
            selectedCategory: null,
            cart: JSON.parse(localStorage.getItem('anuaari_cart')) || [],
            products: [],
            categories: []
        };

        // Fallback sample data in case sheet is offline
        const fallbackProducts = [
            { id: "AB0001", name: "Hanging Beads Oval Shape Readymade Hook Glassy Color", category: "Beads", price: "90.00", colors: "Red, Blue, Green, Gold", image: "", stock: "In Stock" },
            { id: "AB0002", name: "Zari Thread Metallic Gold & Silver Zari Roll", category: "Threads", price: "120.00", colors: "Gold, Silver, Antique Gold", image: "", stock: "In Stock" },
            { id: "AB0003", name: "Aari Embroidery Needle Holder Wooden Handle Set", category: "Tools & Hooks", price: "150.00", colors: "Standard", image: "", stock: "In Stock" },
            { id: "AB0004", name: "Kundan Stone Oval Mirror Flatback Acrylic", category: "Stones & Mirrors", price: "75.00", colors: "Multicolor, Clear Crystal", image: "", stock: "In Stock" },
            { id: "AB0005", name: "Silk Thread Lacquered Multibox Combo", category: "Threads", price: "350.00", colors: "Assorted Shades", image: "", stock: "In Stock" },
            { id: "AB0006", name: "Golden Spring Wire (Passing) - 1 Bunch", category: "Wires", price: "110.00", colors: "Gold, Silver", image: "", stock: "In Stock" }
        ];

        window.addEventListener('DOMContentLoaded', () => {
            if (state.user) {
                document.getElementById('loginModal').classList.add('hidden');
                document.getElementById('storeView').classList.remove('hidden');
                document.getElementById('welcomeUserDisplay').innerText = `Welcome, ${state.user}`;
            }
            fetchInventory();
            updateCartBadge();
        });

        function handleLogin(e) {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const rawPhone = document.getElementById('custPhone').value.trim();
            const phone = rawPhone.replace(/\D/g, '');

            if (!name || phone.length !== 10) {
                showToast("Please provide your name and an exact 10-digit mobile number.", "error");
                return;
            }

            state.user = name;
            state.phone = phone;
            localStorage.setItem('anuaari_user', name);
            localStorage.setItem('anuaari_phone', phone);

            // Log login to Google Sheets in background
            try {
                fetch(GOOGLE_SCRIPT_URL, {
                    method: 'POST',
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ Type: "Login", Customer_Name: name, Primary_Phone: phone })
                });
            } catch (err) { console.error(err); }

            document.getElementById('loginModal').classList.add('hidden');
            document.getElementById('storeView').classList.remove('hidden');
            document.getElementById('welcomeUserDisplay').innerText = `Welcome, ${name}`;
            
            showToast("Login Successful! Welcome to ANUAARI MATERIALS.");
            renderStore();
        }

        function handleLogout() {
            localStorage.clear();
            location.reload();
        }

        async function fetchInventory() {
            const sheetCsvUrl = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI";
            try {
                const response = await fetch(sheetCsvUrl);
                const csvText = await response.text();
                parseCSV(csvText);
            } catch (err) {
                console.warn("Using offline fallback inventory due to network error:", err);
                state.products = fallbackProducts;
                processCategories();
                renderStore();
            }
        }

        function parseCSV(text) {
            const lines = text.split('\n');
            const result = [];
            if (lines.length <= 1) {
                state.products = fallbackProducts;
                processCategories();
                renderStore();
                return;
            }

            for (let i = 1; i < lines.length; i++) {
                const line = lines[i].trim();
                if (!line) continue;
                
                // Simple CSV row parser handling quotes
                const row = [];
                let inQuotes = false;
                let currentVal = '';
                for (let char of line) {
                    if (char === '"') {
                        inQuotes = !inQuotes;
                    } else if (char === ',' && !inQuotes) {
                        row.push(currentVal.trim());
                        currentVal = '';
                    } else {
                        currentVal += char;
                    }
                }
                row.push(currentVal.trim());

                if (row.length >= 4) {
                    let cat = row[1] ? row[1].replace(/^"|"$/g, '') : "General";
                    if (!cat || cat.toLowerCase() === 'nan') cat = "General";
                    
                    let img = row[5] ? row[5].replace(/^"|"$/g, '') : "";
                    let colors = row[4] ? row[4].replace(/^"|"$/g, '') : "";

                    result.push({
                        id: row[0] ? row[0].replace(/^"|"$/g, '') : `PROD${i}`,
                        category: cat,
                        name: row[2] ? row[2].replace(/^"|"$/g, '') : "Craft Item",
                        price: row[3] ? row[3].replace(/^"|"$/g, '') : "99.00",
                        colors: colors,
                        image: img,
                        stock: "In Stock"
                    });
                }
            }

            state.products = result.length > 0 ? result : fallbackProducts;
            processCategories();
            renderStore();
        }

        function processCategories() {
            const cats = [...new Set(state.products.map(p => p.category))];
            state.categories = cats.length > 0 ? cats : ["General"];
            if (!state.selectedCategory || !state.categories.includes(state.selectedCategory)) {
                state.selectedCategory = state.categories[0];
            }
        }

        function switchView(viewName) {
            state.currentView = viewName;
            const homeSec = document.getElementById('homeSection');
            const cartSec = document.getElementById('cartSection');
            const homeBtn = document.getElementById('navHomeBtn');
            const cartBtn = document.getElementById('navCartBtn');

            if (viewName === 'Home') {
                homeSec.classList.remove('hidden');
                cartSec.classList.add('hidden');
                homeBtn.className = "px-4 py-2 rounded-xl text-sm font-bold bg-plum text-white transition shadow-sm";
                cartBtn.className = "px-4 py-2 rounded-xl text-sm font-bold bg-plum-surface text-plum border border-plum-border hover:bg-plum/10 transition relative";
                renderStore();
            } else {
                homeSec.classList.add('hidden');
                cartSec.classList.remove('hidden');
                cartBtn.className = "px-4 py-2 rounded-xl text-sm font-bold bg-plum text-white transition shadow-sm";
                homeBtn.className = "px-4 py-2 rounded-xl text-sm font-bold bg-plum-surface text-plum border border-plum-border hover:bg-plum/10 transition relative";
                renderCart();
            }
        }

        function renderStore() {
            renderCategories();
            renderProducts();
        }

        function renderCategories() {
            const container = document.getElementById('categoryContainer');
            container.innerHTML = '';

            state.categories.forEach(cat => {
                const isSelected = state.selectedCategory === cat;
                const btn = document.createElement('button');
                btn.className = `px-5 py-2.5 rounded-xl text-xs font-extrabold uppercase tracking-wider whitespace-nowrap transition shadow-xs ${
                    isSelected 
                        ? 'bg-plum text-white shadow-plum/20' 
                        : 'bg-white text-gray-700 border border-plum-border hover:bg-plum-surface'
                }`;
                btn.innerHTML = isSelected ? `<i class="fa-solid fa-folder-open mr-1.5 text-gold"></i> ${cat}` : cat;
                btn.onclick = () => {
                    state.selectedCategory = cat;
                    renderStore();
                };
                container.appendChild(btn);
            });
        }

        function renderProducts() {
            const grid = document.getElementById('productGrid');
            grid.innerHTML = '';

            const filtered = state.products.filter(p => p.category === state.selectedCategory);
            document.getElementById('currentCategoryTitle').innerText = state.selectedCategory;
            document.getElementById('productCountBadge').innerText = `${filtered.length} items`;

            if (filtered.length === 0) {
                grid.innerHTML = `<div class="col-span-full text-center py-16 text-gray-500 font-semibold bg-white rounded-2xl border border-plum-border">No items found in this category.</div>`;
                return;
            }

            filtered.forEach((prod, idx) => {
                const card = document.createElement('div');
                card.className = "bg-white rounded-2xl border border-plum-border p-4 product-card flex flex-col justify-between shadow-xs";

                // Image container
                const imgContainer = document.createElement('div');
                imgContainer.className = "w-full h-48 bg-[#fcf9fb] rounded-xl flex items-center justify-center p-2 mb-3 overflow-hidden relative";
                
                if (prod.image && prod.image.toLowerCase() !== 'nan') {
                    const img = document.createElement('img');
                    img.src = prod.image;
                    img.alt = prod.name;
                    img.className = "w-full h-full object-contain object-center rounded-lg";
                    img.onerror = () => {
                        imgContainer.innerHTML = `<div class="text-xs font-bold text-gray-400">Image Preview</div>`;
                    };
                    imgContainer.appendChild(img);
                } else {
                    imgContainer.innerHTML = `<div class="text-xs font-bold text-gray-400">No Image Available</div>`;
                }

                // Title
                const title = document.createElement('div');
                title.className = "font-bold text-xs text-gray-900 h-10 overflow-hidden leading-snug mb-2";
                title.innerText = prod.name;

                // Price
                const priceDiv = document.createElement('div');
                priceDiv.className = "font-extrabold text-sm text-red-600 mb-3 flex items-center gap-2";
                priceDiv.innerHTML = `Rs. ${prod.price} <span class="text-[10px] text-gray-400 line-through font-semibold">Rs. 160.00</span>`;

                // Color options select if available
                let colorSelectHTML = '';
                const colors = prod.colors ? prod.colors.split(',').map(c => c.trim()).filter(Boolean) : [];
                if (colors.length > 0) {
                    colorSelectHTML = `
                        <div class="mb-3">
                            <select id="colorSel_${idx}" class="w-full px-3 py-2 text-xs font-semibold rounded-xl border border-gray-200 bg-gray-50 focus:outline-none focus:ring-1 focus:ring-plum">
                                ${colors.map(c => `<option value="${c}">${c}</option>`).join('')}
                            </select>
                        </div>
                    `;
                }

                // Add to Cart Button
                const btnText = colors.length > 0 ? "Select & Add" : "Add To Cart";
                const btn = document.createElement('button');
                btn.className = "w-full py-2.5 bg-gradient-to-r from-plum to-plum-dark text-white font-bold rounded-xl text-xs uppercase tracking-wider shadow-sm hover:opacity-95 transition";
                btn.innerHTML = `<i class="fa-solid fa-cart-plus mr-1"></i> ${btnText}`;
                btn.onclick = () => {
                    let selectedColor = colors.length > 0 ? document.getElementById(`colorSel_${idx}`).value : "Standard";
                    addToCart(prod.name, selectedColor, prod.price);
                };

                card.appendChild(imgContainer);
                card.appendChild(title);
                card.appendChild(priceDiv);
                if (colors.length > 0) {
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = colorSelectHTML;
                    card.appendChild(tempDiv.firstElementChild);
                }
                card.appendChild(btn);

                grid.appendChild(card);
            });
        }

        function addToCart(productName, color, price) {
            const itemDesc = `${productName} (${color})`;
            state.cart.push({ product: itemDesc, price: price, quantity: "1 Units" });
            localStorage.setItem('anuaari_cart', JSON.stringify(state.cart));
            updateCartBadge();
            showToast("Added to cart successfully!");
        }

        function updateCartBadge() {
            document.getElementById('cartBadge').innerText = state.cart.length;
        }

        function renderCart() {
            const list = document.getElementById('cartItemsList');
            const emptyState = document.getElementById('emptyCartState');
            const checkoutWrapper = document.getElementById('checkoutFormWrapper');
            list.innerHTML = '';

            if (state.cart.length === 0) {
                emptyState.classList.remove('hidden');
                checkoutWrapper.classList.add('hidden');
                return;
            }

            emptyState.classList.add('hidden');
            checkoutWrapper.classList.remove('hidden');

            state.cart.forEach((item, index) => {
                const row = document.createElement('div');
                row.className = "py-3 flex items-center justify-between gap-4";
                row.innerHTML = `
                    <div class="flex items-center gap-3">
                        <div class="w-8 h-8 rounded-full bg-plum/10 text-plum flex items-center justify-center font-bold text-xs">
                            ${index + 1}
                        </div>
                        <div>
                            <p class="text-xs font-bold text-gray-900">${item.product}</p>
                            <p class="text-[11px] text-gray-500 font-semibold">Qty: 1 Unit</p>
                        </div>
                    </div>
                    <button onclick="removeFromCart(${index})" class="text-xs font-bold text-red-600 hover:text-red-800 px-3 py-1.5 rounded-lg hover:bg-red-50 transition">
                        <i class="fa-solid fa-trash mr-1"></i> Remove
                    </button>
                `;
                list.appendChild(row);
            });
        }

        function removeFromCart(index) {
            state.cart.splice(index, 1);
            localStorage.setItem('anuaari_cart', JSON.stringify(state.cart));
            updateCartBadge();
            renderCart();
            showToast("Item removed from cart.");
        }

        function handleCheckout(e) {
            e.preventDefault();
            if (state.cart.length === 0) {
                showToast("Your cart is empty.", "error");
                return;
            }

            const address = document.getElementById('checkoutAddress').value.trim();
            const secPhone = document.getElementById('checkoutSecPhone').value.trim();
            const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
            const notes = document.getElementById('checkoutNotes').value.trim();

            if (!address || secPhone.length !== 10) {
                showToast("Please provide a valid address and 10-digit alternative number.", "error");
                return;
            }

            const cartSummary = state.cart.map(i => i.product).join(', ');
            const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);

            const orderPayload = {
                Type: "Order",
                Timestamp: timestamp,
                Customer_Name: state.user,
                Primary_Phone: state.phone,
                Items: cartSummary,
                Address: address,
                Payment_Method: paymentMethod,
                Secondary_Phone: secPhone,
                Description: notes
            };

            // Post order to Google Sheets
            try {
                fetch(GOOGLE_SCRIPT_URL, {
                    method: 'POST',
                    mode: 'no-cors',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(orderPayload)
                });
            } catch (err) { console.error(err); }

            state.cart = [];
            localStorage.setItem('anuaari_cart', JSON.stringify(state.cart));
            updateCartBadge();

            showToast(`Order placed successfully (${paymentMethod})!`);
            switchView('Home');
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById('toastNotification');
            const msgEl = document.getElementById('toastMessage');
            msgEl.innerText = message;
            
            toast.classList.remove('translate-y-20', 'opacity-0');
            setTimeout(() => {
                toast.classList.add('translate-y-20', 'opacity-0');
            }, 3500);
        }
    </script>
</body>
</html>
