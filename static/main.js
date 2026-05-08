// för fetch()
document.addEventListener("click", async (e) => {
  if (e.target.matches(".like-button")) {
    const commentId = e.target.dataset.commentId;
    const response = await fetch(`/comment/${commentId}/like`, {
      method: "POST"
    });

    const data = await response.json();

    if (data.success) {
      document.getElementById(`like-count-${commentId}`)
      e.target.classList.add("green")
      const element = document.getElementById(`like-count-${commentId}`);
      element.textContent = `Likes: ${data.likes}`;
    }

  }})




// bara för utseende:
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
