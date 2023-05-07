let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {country: ['in']},
    })
// function to specify what should happen when the prediction is clicked

autocomplete.addListener('place_changed', onPlaceChanged);
// enableEnterKey(document.getElementById('id_address'))
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
                        response.cart_amount['tax_dict'],
                        response.cart_amount['grand_total']
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
                        response.cart_amount['tax_dict'],
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
                        response.cart_amount['tax_dict'],
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
    function applyCartAmount(subtotal, tax_dict, grand_total){
        if(window.location.pathname == '/cart/'){
            $('#subtotal').html(subtotal)
            
            $('#total').html(grand_total)

            for(key1 in tax_dict){
                for(key2 in tax_dict[key1]){
                    $('#tax-'+key1).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // Add opening hours
    $('.add_hours').on('click', function(e){
        e.preventDefault();
        var day = document.getElementById('id_day').value
        var from_hour = document.getElementById('id_from_hour').value
        var to_hour = document.getElementById('id_to_hour').value
        var is_closed = document.getElementById('id_is_closed').checked
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val()

        var url = document.getElementById('add_hour_url').value

        if(is_closed){
            is_closed = 'True'
            condition = "day != ''"

        }else{
            is_closed = 'False'
            condition = "day != '' && from_hour != '' && to_hour != ''"
        }

        if(eval(condition)){
            $.ajax({
                type : 'POST',
                url : url,
                data: {
                    'day':day,
                    'from_hour':from_hour,
                    'to_hour':to_hour,
                    'is_closed':is_closed,
                    'csrfmiddlewaretoken':csrf_token,
                },
                success: function(response){
                    if(response.status == 'success'){
                        if(response.is_closed == 'Closed'){
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>Closed</td><td><a href="#" class="rmv_hours" data-url="/vendor/opening_hours/add/remove/'+response.id+'/">Remove</a></td></tr>'
                        }else{
                            html = '<tr id="hour-'+response.id+'"><td><b>'+response.day+'</b></td><td>'+response.from_hour+' - '+response.to_hour+'</td><td><a href="#" class="rmv_hours" data-url="/vendor/opening_hours/add/remove/'+response.id+'/">Remove</a></td></tr>'
                        }
                        
                        $('.opening_hours').append(html)
                        document.getElementById('opening_hours').reset();
                    }else{
                        swal(response.message,'',"error");
                    }
                }

            })
        }else{
            swal('Please fill all fields','','info');
        }
    })
    // Remove opening hours
    // $('.rmv_hours').on('click',function(e){
    //     e.preventDefault();
        
    // })

    $(document).on('click','.rmv_hours', function(e){
        e.preventDefault();
        url = $(this).attr('data-url');
        console.log(url)
        $.ajax({
            type:'GET',
            url:url,
            success: function(response){
                if(response.status == 'success'){
                    document.getElementById('hour-'+response.id).remove()
                }
            }
        })
    })

    // document ready close
});