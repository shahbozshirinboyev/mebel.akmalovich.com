document.addEventListener("DOMContentLoaded", function () {
  // console.log("user_autofill.js loaded successfully");

  const userSelect = document.querySelector("#id_user");
  const fullNameField = document.querySelector("#id_full_name");
  const phoneField = document.querySelector("#id_phone_number");

  // console.log("Elements found:", { userSelect: !!userSelect, fullNameField: !!fullNameField, phoneField: !!phoneField, });

  if (!userSelect) {
    // console.warn("user_autofill: user dropdown not found");
    return;
  }

  userSelect.addEventListener("change", function () {
    const userId = this.value;
    // console.log("User selected:", userId);

    if (!userId) {
      // console.log("No user selected, clearing fields");
      if (fullNameField) fullNameField.value = "";
      if (phoneField) phoneField.value = "";
      return;
    }

    // Absolute URL to the admin endpoint
    const url = `/admin/salary/employee/get-user-details/${userId}/`;
    // console.log("Fetching from:", url);

    fetch(url)
      .then((response) => {
        // console.log("Response status:", response.status);
        if (!response.ok) {
          return response.text().then((text) => {
            throw new Error(`HTTP ${response.status}: ${text}`);
          });
        }
        return response.json();
      })
      .then((data) => {
        // console.log("User data received:", data);
        if (fullNameField) {
          fullNameField.value = data.full_name || "";
          // console.log("full_name set to:", data.full_name);
        }
        if (phoneField) {
          phoneField.value = data.phone_number || "";
          // console.log("phone_number set to:", data.phone_number);
        }
      })
      .catch((error) => {
        console.error("Error fetching user details:", error);
      });
  });
});
