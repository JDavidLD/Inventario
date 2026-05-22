// Sidebar toggle
document.addEventListener('DOMContentLoaded', function () {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('page-content');
  if (toggle) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      content.classList.toggle('expanded');
    });
  }
});

// Generic barcode input handler for forms
// Listens on an input[data-barcode] and calls /productos/buscar_codigo
function initBarcodeInput(inputId, callback) {
  const input = document.getElementById(inputId);
  if (!input) return;
  let debounce;
  input.addEventListener('input', function () {
    clearTimeout(debounce);
    const val = this.value.trim();
    if (!val) return;
    debounce = setTimeout(() => {
      fetch(`/productos/buscar_codigo?codigo=${encodeURIComponent(val)}`)
        .then(r => r.json())
        .then(data => callback(data));
    }, 400);
  });
}

// Format currency
function formatCOP(n) {
  return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(n);
}
