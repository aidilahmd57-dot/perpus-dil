// Auto-hide flash messages
document.addEventListener('DOMContentLoaded', function () {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (f) {
    setTimeout(function () {
      f.style.transition = 'opacity .5s';
      f.style.opacity = '0';
      setTimeout(function () { f.remove(); }, 500);
    }, 3000);
  });

  // Cover upload preview
  const coverInput = document.getElementById('coverInput');
  if (coverInput) {
    coverInput.addEventListener('change', function () {
      previewImage(this, 'coverPreviewImg', 'coverPreviewBox', 'coverPreviewLabel');
    });
  }

  // Cover drag & drop
  const dropZone = document.getElementById('coverDropZone');
  if (dropZone) {
    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      this.style.borderColor = 'var(--purple)';
      this.style.background = '#F0E8FF';
    });
    dropZone.addEventListener('dragleave', function () {
      this.style.borderColor = '';
      this.style.background = '';
    });
    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      this.style.borderColor = '';
      this.style.background = '';
      const file = e.dataTransfer.files[0];
      if (file) {
        const dt = new DataTransfer();
        dt.items.add(file);
        coverInput.files = dt.files;
        previewImage(coverInput, 'coverPreviewImg', 'coverPreviewBox', 'coverPreviewLabel');
      }
    });
  }

  // Star rating input
  const stars = document.querySelectorAll('.star-btn');
  const ratingInput = document.getElementById('ratingInput');
  stars.forEach(function (star) {
    star.addEventListener('click', function () {
      const val = parseInt(this.dataset.val);
      if (ratingInput) ratingInput.value = val;
      stars.forEach(function (s) {
        s.textContent = parseInt(s.dataset.val) <= val ? '★' : '☆';
        s.classList.toggle('active', parseInt(s.dataset.val) <= val);
      });
    });
  });

  // Confirm delete
  document.querySelectorAll('.confirm-delete').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      if (!confirm('Yakin ingin menghapus ini?')) e.preventDefault();
    });
  });
});

function previewImage(input, imgId, boxId, labelId) {
  const file = input.files[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    alert('File harus berupa gambar!');
    input.value = '';
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    alert('Ukuran gambar terlalu besar! Maks 5MB.');
    input.value = '';
    return;
  }
  const reader = new FileReader();
  reader.onload = function (e) {
    const img = document.getElementById(imgId);
    const box = document.getElementById(boxId);
    const lbl = document.getElementById(labelId);
    if (img) img.src = e.target.result;
    if (box) box.style.display = 'block';
    if (lbl) lbl.textContent = '✅ ' + file.name + ' (' + (file.size / 1024).toFixed(0) + ' KB)';
  };
  reader.readAsDataURL(file);
}
