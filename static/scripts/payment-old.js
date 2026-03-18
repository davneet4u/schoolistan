// --------------- Payments ---------------
const payNow = async () => {
  document.getElementById("loader").style.display = "block";
  const res = await fetch("/payments/create-order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
    },
    body: JSON.stringify({}),
  });
  document.getElementById("loader").style.display = "none";
  if (res.status === 201) {
    const jsonData = await res.json();
    startRazorpay(jsonData.data);
  } else if (res.redirected) {
    window.location.href = "/login/?next=/pricing/";
  } else {
    alert((await res.json()).detail);
  }
};
const startRazorpay = (data) => {
  let options = {
    key: data.key, // Enter the Key ID generated from the Dashboard
    amount: data.amount.toString(), // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    currency: "INR",
    name: "IRAH Solutions",
    description: "Test Transaction",
    image: "",
    order_id: data.rzp_order_id, //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
    handler: function (response) {
      //   alert(response.razorpay_payment_id);
      //   alert(response.razorpay_order_id);
      //   alert(response.razorpay_signature);
      postPaymentSuccess(
        response.razorpay_payment_id,
        response.razorpay_order_id,
        response.razorpay_signature
      );
    },
    prefill: {
      name: data.name,
      email: data.email,
      contact: data.contact,
    },
    // notes: {
    //   address: "Razorpay Corporate Office",
    // },
    theme: {
      color: "#3399cc",
    },
  };
  let rzp1 = new Razorpay(options);
  rzp1.on("payment.failed", function (response) {
    console.log("code: ", response.error.code);
    console.log("description: ", response.error.description);
    console.log("source: ", response.error.source);
    console.log("step: ", response.error.step);
    console.log("reason: ", response.error.reason);
    console.log("order_id: ", response.error.metadata.order_id);
    console.log("payment_id: ", response.error.metadata.payment_id);
  });
  rzp1.open();
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
