  // Copy summary data to clipboard or show modal fallback
  const copyBtn = document.getElementById('copySummaryBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      const summary = [
        `Total Trips: ${document.getElementById('totalTrips')?.textContent}`,
        `Total Room Nights: ${document.getElementById('totalNights')?.textContent}`,
        `Unique Traveler: ${document.getElementById('uniqueTravelers')?.textContent}`,
        `Unique Property: ${document.getElementById('uniqueProperties')?.textContent}`
      ].join('\n');
      // Try clipboard API first
      if (navigator.clipboard) {
        navigator.clipboard.writeText(summary).then(() => {
          copyBtn.textContent = 'Copied!';
          setTimeout(() => { copyBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy Data'; }, 1200);
        }, () => showModal(summary));
      } else {
        showModal(summary);
      }
      function showModal(text) {
        const modalText = document.getElementById('copyModalText');
        if (modalText) {
          modalText.value = text;
          if (window.bootstrap && bootstrap.Modal) {
            var modal = new bootstrap.Modal(document.getElementById('copyModal'));
            modal.show();
          }
        }
      }
    });
  }
document.addEventListener('DOMContentLoaded', function () {
  // Table data copy logic
  // Row copy logic for formatted output (click name cell)
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('copyRowCell')) {
      const cell = e.target;
      const row = cell.closest('tr');
      if (row) {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
          const formatted =
            `Name: ${cells[0].textContent.trim()}` + '\n' +
            `Accommodation: ${cells[1].textContent.trim()}` + '\n' +
            `Arrival: ${cells[2].textContent.trim()}` + '\n' +
            `Departure: ${cells[3].textContent.trim()}` + '\n' +
            `Night Stayed: ${cells[4].textContent.trim()}` + '\n' +
            `Itinerary Type: ${cells[5].textContent.trim()}`;
          if (navigator.clipboard) {
            navigator.clipboard.writeText(formatted).then(() => {
              cell.textContent = 'Copied!';
              setTimeout(() => { cell.textContent = formatted.split('\n')[0].replace('Name: ', ''); }, 1200);
            }, () => showModal(formatted));
          } else {
            showModal(formatted);
          }
        }
      }
    }
  });

  document.querySelectorAll('#copyTableBtn').forEach(function(copyTableBtn) {
    copyTableBtn.addEventListener('click', function () {
      const table = document.getElementById('dataTable');
      let tableText = '';
      if (table) {
        // Get header
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
        tableText += headers.join('\t') + '\n';
        // Get only visible rows
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
          if (row.style.display === 'none') return;
          const cells = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
          tableText += cells.join('\t') + '\n';
        });
      }
      if (navigator.clipboard) {
        navigator.clipboard.writeText(tableText).then(() => {
          copyTableBtn.textContent = 'Copied!';
          setTimeout(() => { copyTableBtn.innerHTML = '<i class="bi bi-clipboard"></i> Copy Table'; }, 1200);
        }, () => showModal(tableText));
      } else {
        showModal(tableText);
      }
      function showModal(text) {
        const modalText = document.getElementById('copyModalText');
        if (modalText) {
          modalText.value = text;
          if (window.bootstrap && bootstrap.Modal) {
            var modal = new bootstrap.Modal(document.getElementById('copyModal'));
            modal.show();
          }
        }
      }
    });
  });
  // Measure fixed header height and set CSS var so layout stays correct
  const header = document.getElementById('appHeader');
  if (header) {
    const h = header.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--header-h', `${Math.round(h)}px`);
  }

  const searchInput = document.getElementById('searchInput');
  const table = document.getElementById('dataTable');
  const rows = table ? table.getElementsByTagName('tr') : [];

  if (searchInput && table) {
    searchInput.addEventListener('keyup', function () {
      const filter = searchInput.value.toLowerCase();
      let totalTrips = 0;
      let totalNights = 0;
      const travelers = new Set();
      const properties = new Set();

      for (let i = 1; i < rows.length; i++) {
        const tr = rows[i];
        const cells = tr.getElementsByTagName('td');
        if (!cells || cells.length === 0) continue; // skip header row

        let match = false;
        for (let j = 0; j < cells.length; j++) {
          if (cells[j].innerText.toLowerCase().includes(filter)) { match = true; break; }
        }

        if (match) {
          tr.style.display = '';
          totalTrips++;
          const nights = parseInt(cells[4].innerText.replace(/[^\d\-]/g, ''), 10);
          totalNights += Number.isFinite(nights) ? nights : 0;
          travelers.add(cells[0].innerText);
          properties.add(cells[1].innerText);
        } else {
          tr.style.display = 'none';
        }
      }
      const tTrips = document.getElementById('totalTrips');
      const tNights = document.getElementById('totalNights');
      const uTrav = document.getElementById('uniqueTravelers');
      const uProp = document.getElementById('uniqueProperties');
      if (tTrips) tTrips.innerText = totalTrips;
      if (tNights) tNights.innerText = totalNights;
      if (uTrav) uTrav.innerText = travelers.size;
      if (uProp) uProp.innerText = properties.size;
    });
  }

  const clearBtn = document.getElementById('clearFilter');
  if (clearBtn) {
    clearBtn.addEventListener('click', function (e) {
      // Let navigation happen; no need to preventDefault
      // This resets filters server-side and reloads the page
    });
  }

  const filterBtn = document.getElementById('filterBtn');
  if (filterBtn) {
    filterBtn.addEventListener('click', function () {
      showToast('Filters applied successfully!');
    });
  }
  const updateBtn = document.getElementById('updateBtn');
  if (updateBtn) {
    updateBtn.addEventListener('click', function () {
      showToast('Data updated successfully!');
    });
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast-message';
    toast.innerText = message;
    document.body.appendChild(toast);
    setTimeout(() => { toast.remove(); }, 3000);
  }
});
