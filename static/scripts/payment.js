// --------------- Payments ---------------
const cashfree = Cashfree({
  mode: CASH_FREE_MODE, // sandbox or production
});

const payNow = async (product_type, product_ids) => {
  // document.getElementById("loader").style.display = "block";
  const res = await fetch("/payments/create-order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
    },
    body: JSON.stringify({product_type: product_type, product_ids: product_ids}),
  });
  // document.getElementById("loader").style.display = "none";
  if (res.status === 201) {
    const jsonData = await res.json();
    startCashfree(jsonData.data);
  } else if (res.redirected) {
    window.location.href = "/login/?next=/pricing/";
  } else {
    alert((await res.json()).msg);
  }
};
const startCashfree = (data) => {

  let checkoutOptions = {
    paymentSessionId: data.payment_session_id,
    mode: data.mode,
    returnUrl: data.return_url,
  };

  cashfree.checkout(checkoutOptions).then(function (result) {
    if (result.error) {
      alert(result.error.message);
    }
    if (result.redirect) {
      console.log("Redirection");
    }
  });

};
const postPaymentSuccess = async (
  razorpay_payment_id,
  razorpay_order_id,
  razorpay_signature
) => {
  const res = await fetch("/payments/success", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
    },
    body: JSON.stringify({
      razorpay_payment_id: razorpay_payment_id,
      razorpay_order_id: razorpay_order_id,
      razorpay_signature: razorpay_signature,
    }),
  });
  if (res.status === 200) {
    const jsonData = await res.json();
    window.location.href = "/dashboard/";
  } else {
    alert((await res.json()).detail);
  }
};
