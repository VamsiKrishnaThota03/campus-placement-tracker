/* Client-side filter for tables: <input data-filter-table="tableId"> */
document.querySelectorAll('[data-filter-table]').forEach(function (input) {
  const table = document.getElementById(input.dataset.filterTable);
  if (!table) return;
  const empty = table.parentElement.querySelector('[data-no-results]');
  input.addEventListener('input', function () {
    const query = input.value.trim().toLowerCase();
    let shown = 0;
    table.querySelectorAll('tbody tr').forEach(function (row) {
      const match = row.textContent.toLowerCase().includes(query);
      row.hidden = !match;
      if (match) shown++;
    });
    if (empty) empty.classList.toggle('d-none', shown > 0);
  });
});
