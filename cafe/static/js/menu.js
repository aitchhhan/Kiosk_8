document.addEventListener('DOMContentLoaded', function() {
  const menuButtons = document.querySelectorAll('.menu-categories li a');
  const menuItems = document.querySelectorAll('.menu-items .category');
  const itemModal = document.getElementById('itemModal');
  const closeModal = document.querySelector('.modal .close');
  const itemForm = document.getElementById('itemForm');

  let selectedItem = null;

  menuButtons.forEach(button => {
      button.addEventListener('click', function(event) {
          event.preventDefault();
          menuButtons.forEach(btn => btn.classList.remove('active'));
          button.classList.add('active');

          const category = button.getAttribute('href').replace('#', '');
          menuItems.forEach(item => {
              if (item.classList.contains(category)) {
                  item.style.display = 'block';
              } else {
                  item.style.display = 'none';
              }
          });
      });
  });

  document.querySelectorAll('.stampBtn').forEach(button => {
      button.addEventListener('click', function() {
          selectedItem = {
              name: this.dataset.name,
              price: this.dataset.price
          };
          itemModal.style.display = 'block';
      });
  });

  closeModal.addEventListener('click', function() {
      itemModal.style.display = 'none';
  });

  window.addEventListener('click', function(event) {
      if (event.target == itemModal) {
          itemModal.style.display = 'none';
      }
  });

  itemForm.addEventListener('submit', function(event) {
      event.preventDefault();
      const formData = new FormData(itemForm);
      const itemDetails = {
          name: selectedItem.name,
          price: selectedItem.price,
          container: formData.get('container'),
          temperature: formData.get('temperature'),
          size: formData.get('size'),
          quantity: parseInt(formData.get('quantity'))
      };

      addItemToCart(itemDetails);
      itemModal.style.display = 'none';
      itemForm.reset();
  });

  function addItemToCart(item) {
      const cart = document.querySelector('.cart ul');
      const cartItem = document.createElement('li');
      cartItem.className = 'cart-item';
      cartItem.innerHTML = `
          <div class="item-info">
              <h3>${item.name} (${item.container}, ${item.temperature}, ${item.size})</h3>
              <span class="quantity">x<span class="item-quantity">${item.quantity}</span></span>
              <span class="price">${item.price * item.quantity}원</span>
          </div>
          <div class="cart-controls">
              <button class="increaseBtn">+</button>
              <button class="decreaseBtn">-</button>
              <button class="removeBtn">Remove</button>
          </div>
      `;
      cart.appendChild(cartItem);

      const increaseBtn = cartItem.querySelector('.increaseBtn');
      const decreaseBtn = cartItem.querySelector('.decreaseBtn');
      const removeBtn = cartItem.querySelector('.removeBtn');

      updateDecreaseButton(decreaseBtn, item.quantity);

      increaseBtn.addEventListener('click', function() {
          item.quantity += 1;
          updateCartItem(cartItem, item);
      });

      decreaseBtn.addEventListener('click', function() {
          if (item.quantity > 1) {
              item.quantity -= 1;
              updateCartItem(cartItem, item);
          }
      });

      removeBtn.addEventListener('click', function() {
          cartItem.remove();
          updateTotal();
      });

      updateTotal();
  }

  function updateCartItem(cartItem, item) {
      cartItem.querySelector('.item-quantity').textContent = item.quantity;
      cartItem.querySelector('.price').textContent = `${item.price * item.quantity}원`;
      updateDecreaseButton(cartItem.querySelector('.decreaseBtn'), item.quantity);
      updateTotal();
  }

  function updateDecreaseButton(button, quantity) {
      if (quantity <= 1) {
          button.disabled = true;
      } else {
          button.disabled = false;
      }
  }

  function updateTotal() {
      const cartItems = document.querySelectorAll('.cart .cart-item');
      let total = 0;
      cartItems.forEach(item => {
          const price = parseInt(item.querySelector('.price').textContent.replace('원', ''));
          total += price;
      });
      document.querySelector('.cart .total .price').textContent = `${total}원`;
  }
});