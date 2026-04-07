// ── Flash auto-dismiss ──────────────────────────────────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => el.remove(), 5000);
  el.addEventListener('click', () => el.remove());
});

// ── Seat selection logic ────────────────────────────────────
const selectedSeats = new Set();

function initSeatGrid() {
  const seats = document.querySelectorAll('.seat.available');
  const totalEl = document.getElementById('total-display');
  const countEl = document.getElementById('count-display');
  const hiddenInput = document.getElementById('selected-seats-input');
  const buyBtn = document.getElementById('buy-btn');
  const precioUnitario = parseFloat(document.getElementById('precio-unitario')?.value || 0);

  seats.forEach(seat => {
    seat.addEventListener('click', () => {
      const id = seat.dataset.id;
      if (selectedSeats.has(id)) {
        selectedSeats.delete(id);
        seat.classList.remove('selected');
      } else {
        selectedSeats.add(id);
        seat.classList.add('selected');
      }
      updateSummary();
    });
  });

  function updateSummary() {
    const count = selectedSeats.size;
    if (countEl) countEl.textContent = count;
    if (totalEl) totalEl.textContent = formatCurrency(count * precioUnitario);
    if (hiddenInput) hiddenInput.value = Array.from(selectedSeats).join(',');
    if (buyBtn) buyBtn.disabled = count === 0;
  }

  updateSummary();
}

function formatCurrency(val) {
  return '$' + Math.round(val).toLocaleString('es-CO');
}

// ── Confirm delete dialogs ──────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// ── QR Code generation (on ticket page) ────────────────────
function generateQR(code, canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof QRCode === 'undefined') return;
  QRCode.toCanvas(canvas, code, { width: 180, margin: 2, color: { dark: '#000000', light: '#ffffff' } });
}

// ── Admin: highlight active sidebar link ────────────────────
(function() {
  const path = window.location.pathname;
  document.querySelectorAll('.admin-nav-link').forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
})();

// ── Init on DOM ready ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initSeatGrid();
});
