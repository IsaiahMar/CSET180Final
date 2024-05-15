let cart = {};

if (localStorage.getItem("cart")) {
    cart = JSON.parse(sessionStorage.getItem("cart"));
    displayCartItems();
    updateCartTotal();
}


function addToCart(item) {
    var parentElement = item.parentNode;
    var itemName = parentElement.children[0].textContent;
    var itemPrice = parentElement.children[2].textContent;
    if (cart[itemName]) {
        alert(`${itemName} is already in the cart!`);
    } else {
        cart[itemName] = { price: itemPrice, quantity: 1 };
        displayCartItems();
        updateCartTotal();
        localStorage.setItem("cart", JSON.stringify(cart));
        alert(`${itemName} is added to the cart!`);
    }
}
function generate(){
    var result = '';

    result += document.getElementsByClassName('drop').value + ' - ';
    result += document.getElementById('text2').value;

	document.getElementById('output').innerHTML = result;
}
generate();   
document.getElementById('submit').onclick = function(){
            var selectedValues = [];
            for(var option of document.getElementById('color').options){
                if(option.selected){
                    selectedValues.push(option.value)
                }
            }
        }
function login() {
    let email = document.getElementById("email").value;
    let pass = document.getElementById("pass").value;

    if (localStorage.getItem(email)) {
        if (pass == localStorage.getItem(email)) {
            location.replace("menu.html");
            alert("Login Successful");
        } else if (pass == "") {
            alert("Login Failed please enter your password");
        }
    } else if (email == "") {
        alert("Login Failed please enter your email");
    } else if (localStorage.getItem(email) == null || pass == "") {
        alert("Login Failed Unknown credential combination");
    }
}
function displayCartItems() {
    const cartItemsContainer = document.querySelector(".cart-items");
    cartItemsContainer.innerHTML = "";

    for (let itemName in cart) {
        const item = cart[itemName];
        const cartRow = document.createElement("div");
        cartRow.classList.add("cart-row");
        const cartRowHTML = `
        <div class="cart-item cart-column">
          <span class="cart-item-title">${itemName}</span>
        </div>
        <span class="cart-price cart-column">${(item.price)}</span>
        <div class="cart-quantity cart-column">
          <input class="cart-quantity-input" type="number" min = 1 value="${
            item.quantity
          }" data-item-name="${itemName}">
          <button onclick="removeFromCart('${itemName}')" class="btn btn-danger">REMOVE</button>
        </div>
      `;
        cartRow.innerHTML = cartRowHTML;
        cartItemsContainer.append(cartRow);
    }
    let quantityInputs = document.querySelectorAll(".cart-quantity-input");
    quantityInputs.forEach((input) => {
        input.addEventListener("change", (event) => {
            let newQuantity = parseInt(event.target.value);
            var itemName = event.target.getAttribute("data-item-name");
            updateQuantity(itemName, newQuantity);
        });
    });
}
function removeFromCart(itemName) {
    delete cart[itemName];
    displayCartItems();
    updateCartTotal();
    localStorage.setItem("cart", JSON.stringify(cart));
}

function updateCartTotal() {
    let total = 0;

    for (let itemName in cart) {
        price = (cart[itemName].price).substring(1);
        total += parseFloat(price) * cart[itemName].quantity;
    }
    document.querySelector(".cart-total-price").innerText =
        "$" + total.toFixed(2);
}