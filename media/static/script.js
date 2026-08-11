// Contoh interaksi tombol
document.addEventListener("DOMContentLoaded", () => {
  const warningBtn = document.getElementById("btn-warning");
  const dispositionBtn = document.getElementById("btn-disposisi");

  warningBtn?.addEventListener("click", () => {
    alert("Peringatan diklik!");
  });

  dispositionBtn?.addEventListener("click", () => {
    alert("Disposisi diklik!");
  });
});
