/**
 * scanner.js — Wrapper sobre html5-qrcode para escaneo de códigos de barras.
 * 
 * Uso:
 *   ScannerManager.init('scannerModal', 'qr-reader', onResultCallback)
 *   ScannerManager.open()   — abre el modal e inicia la cámara
 *   ScannerManager.stop()   — detiene la cámara
 */

const ScannerManager = (() => {
  let html5QrCode = null;
  let modalEl = null;
  let bsModal = null;
  let onResult = null;
  let running = false;

  function init(modalId, readerId, resultCallback) {
    onResult = resultCallback;
    modalEl = document.getElementById(modalId);
    if (!modalEl) return;

    bsModal = new bootstrap.Modal(modalEl);

    // Stop camera when modal is closed
    modalEl.addEventListener('hide.bs.modal', () => { stop(); });

    const formatos = [
        Html5QrcodeSupportedFormats.QR_CODE,
        Html5QrcodeSupportedFormats.EAN_13,
        Html5QrcodeSupportedFormats.EAN_8,
        Html5QrcodeSupportedFormats.CODE_128,
        Html5QrcodeSupportedFormats.CODE_39,
        Html5QrcodeSupportedFormats.UPC_A,
        Html5QrcodeSupportedFormats.UPC_E,
      ];
    html5QrCode = new Html5Qrcode(readerId, { verbose: false, formatsToSupport: formatos });
  }

  async function open() {
    if (!html5QrCode) { console.warn('Scanner no inicializado'); return; }
    bsModal.show();
    // Small delay to let the modal render before starting camera
    await new Promise(r => setTimeout(r, 400));
    if (running) return;
    try {
      const cameras = await Html5Qrcode.getCameras();
      if (!cameras || cameras.length === 0) {
        alert('No se encontraron cámaras. Asegúrate de dar permiso o usa HTTPS.');
        bsModal.hide();
        return;
      }
      // Prefer back camera on mobile
      const cam = cameras.find(c => /back|rear|environment/i.test(c.label)) || cameras[cameras.length - 1];
      await html5QrCode.start(
        cam.id,
        { fps: 10, qrbox: { width: 250, height: 150 }, aspectRatio: 1.5 },
        (decodedText) => {
          stop();
          bsModal.hide();
          if (onResult) onResult(decodedText);
        },
        () => {} // ignore per-frame errors
      );
      running = true;
    } catch (err) {
      console.error('Error al iniciar cámara:', err);
      let msg = 'No se pudo acceder a la cámara.';
      if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
        msg += '\n\nEl navegador requiere HTTPS para usar la cámara. Accede por localhost o sube la app a Render.';
      } else {
        msg += '\n\nVerifica que diste permiso de cámara al navegador.';
      }
      alert(msg);
      bsModal.hide();
    }
  }

  function stop() {
    if (html5QrCode && running) {
      html5QrCode.stop().catch(() => {});
      running = false;
    }
  }

  return { init, open, stop };
})();
