$('.plus-cart').click(function(){
    console.log('Button clicked');

    var id = $(this).attr('pid').toString();
    var quantityElement = this.parentNode.children[2];

    $.ajax({
        type: 'GET',
        url: '/pluscart',
        data: { cart_id: id },

        success: function(data){
            console.log(data);
            // Update the quantity displayed
            quantityElement.innerText = data.quantity;
            document.getElementById(`quantity${id}`).innerText = data.quantity;
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;
        },
        error: function(error){
            console.log('Error:', error);
        }
    });
});

$('.minus-cart').click(function(){
    console.log('Button clicked');

    var id = $(this).attr('pid').toString();
    var quantityElement = this.parentNode.children[2];

    $.ajax({
        type: 'GET',
        url: '/minuscart',
        data: { cart_id: id },

        success: function(data){
            console.log(data);
            // Update the quantity displayed
            quantityElement.innerText = data.quantity;
            document.getElementById(`quantity${id}`).innerText = data.quantity;
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;
        },
        error: function(error){
            console.log('Error:', error);
        }
    });
});

$('.remove-cart').click(function(){
    var id = $(this).attr('pid').toString();
    var toRemove = this.closest('.cart-item'); // Assuming the cart item is nested within a .cart-item element.

    $.ajax({
        type: 'GET',
        url: '/removecart',
        data: { cart_id: id },

        success: function(data){
            console.log(data);
            // Update the total amount displayed
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;

            // Remove the cart item from the UI
            toRemove.remove();
        },
        error: function(error){
            console.log('Error:', error);
        }
    });
});
