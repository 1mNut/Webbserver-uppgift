document.addEventListener("DOMContentLoaded", function () {
  const button = document.getElementById("profile-button");
  const dropdown = document.getElementById("profile-dropdown");

  if (!button || !dropdown) return;

  button.addEventListener("click", function (event) {
    event.stopPropagation();
    dropdown.classList.toggle("open");
    const expanded = dropdown.classList.contains("open");
    button.setAttribute("aria-expanded", expanded);
    dropdown.setAttribute("aria-hidden", !expanded);
  });

  document.addEventListener("click", function () {
    if (dropdown.classList.contains("open")) {
      dropdown.classList.remove("open");
      button.setAttribute("aria-expanded", "false");
      dropdown.setAttribute("aria-hidden", "true");
    }
  });

  dropdown.addEventListener("click", function (event) {
    event.stopPropagation();
  });
});
