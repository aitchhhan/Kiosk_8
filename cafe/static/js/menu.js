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
          quantity: formData.get('quantity')
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
              <span class="quantity">x${item.quantity}</span>
              <span class="price">${item.price * item.quantity}원</span>
          </div>
          <button class="removeBtn">-</button>
      `;
      cart.appendChild(cartItem);

      cartItem.querySelector('.removeBtn').addEventListener('click', function() {
          cartItem.remove();
          updateTotal();
      });

      updateTotal();
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
