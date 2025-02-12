
const bar = document.getElementById('bar');
const close = document.getElementById('close');
const nav = document.getElementById('navbar');

if(bar){
    bar.addEventListener('click',()=>{
        nav.classList.add('active');
    })
}
if (close){
    close.addEventListener('click',()=>{
        nav.classList.remove('active');
    })
}


const productContainer = document.querySelector('.pro-container');

fetch('http://localhost:5000/products')
    .then(response => response.json())
    .then(products => {
        products.forEach(product => {
            const productDiv = document.createElement('div');
            productDiv.classList.add('pro');

            productDiv.innerHTML = `
                <img src="${product.image_url}" alt="${product.name}">
                <div class="des">
                    <span>Unknown</span>  
                    <h5>${product.name}</h5>
                    <div class="star">
                        <i class="fa fa-star" aria-hidden="true"></i>
                        <i class="fa fa-star" aria-hidden="true"></i>
                        <i class="fa fa-star" aria-hidden="true"></i>
                        <i class="fa fa-star" aria-hidden="true"></i>
                        <i class="fa fa-star" aria-hidden="true"></i>
                    </div>
                    <h4>₹${product.price}</h4>
                </div>
                <a href="#"><i class="fa fa-shopping-cart cart" aria-hidden="true"></i></a>
            `;

            productContainer.appendChild(productDiv);
        });
    })
    .catch(error => console.error('Error fetching products:', error));
