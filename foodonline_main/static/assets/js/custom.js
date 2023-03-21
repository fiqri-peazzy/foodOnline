let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
}

$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        // alert(food_id + "\n" + url);
        data = {
            food_id: food_id,
        };
        $.ajax({
            type: 'GET',
            url: url,
            dataType: "json",
            data: data,
            success: function(response){
                console.log(response);
                if (response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login';
                    })
                }else if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }else {
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);

                    // subtotal, tax and grand total
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['total']
                        )
                }
            }
        })
    })

    // place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)
    })

    
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('id');
        
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response);
                if (response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login';
                    })
                }else if (response.status == 'Failed'){
                    swal(response.message,'','error')
                }else {
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']
                        )
                    if(window.location.pathname == '/cart/'){
                        removeCartitem(response.qty,cart_id)
                        chkEmptyCart();
                    }

                    // subtotal, tax and grand total
                    
                    
                }
                
            }
        })
    })

    // delete cart
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        
        $.ajax({
            type: 'GET',
            url: url,

            success: function(response){
                console.log(response);
                if (response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location = '/login';
                    })
                }else {
                    $('#cart-counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, 'success');
                    
                    applyCartAmount(
                        response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']
                        )

                    removeCartitem(0,cart_id);
                    chkEmptyCart();
                }
                
            }
        })
    })

    // delete thte cart element if qty is 0
    function removeCartitem(cartItemQty,cart_id){
        if(cartItemQty <= 0){
            // remove th cart item element
            document.getElementById("cart-item-"+cart_id).remove();
        }
    }

    function chkEmptyCart(){
        
        var cart_counter = document.getElementById('cart-counter').innerHTML;
        if (cart_counter == 0){
            document.getElementById('empty_cart').style.display = "block";
        }
    }
    // apply cart amount
    function applyCartAmount(subtotal, tax, grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)
        }
    }
});