var stripe = Stripe(checkout_public_key)

const button = document.querySelector('#buy_now_btn');

button.addEventListener('click', event => {
    console.log("Pressed checkout")
    stripe.redirectToCheckout({
        sessionId: checkout_session_id
    }).then(function (result) {

    }
})