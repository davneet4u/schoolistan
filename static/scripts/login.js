// --------------- query parameters ---------------
const params = new Proxy(new URLSearchParams(window.location.search), {
  get: (searchParams, prop) => searchParams.get(prop),
});
// Get the value of "some_key" in eg "https://example.com/?some_key=some_value"
// let value = params.some_key; // "some_value"

// --------------- google login ---------------
window.onload = function () {
  google.accounts.id.initialize({
    client_id: G_CLIENT_ID,
    callback: handleCredentialResponse,
    cancel_on_tap_outside: false,
  });
  google.accounts.id.renderButton(
    document.getElementById("buttonDiv"),
    {
      theme: "filled_blue",
      size: "large",
      shape: "pill",
      text: "continue_with",
    } // customization attributes
  );
  google.accounts.id.prompt(); // also display the One Tap dialog
};
async function handleCredentialResponse(response) {
  // console.log("Encoded JWT ID token: " + response.credential);
  const result = await postToServer("/login", {
    credential: response.credential,
  });
  if (result.status) window.location.href = params.next ? params.next : "/";
  else alertify.error(result.msg);
}
