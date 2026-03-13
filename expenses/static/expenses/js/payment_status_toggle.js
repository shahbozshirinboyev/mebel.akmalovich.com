(function () {
  function normalizeDecimal(raw) {
    if (!raw) return 0;
    const normalized = String(raw).replace(/\s+/g, '').replace(/,/g, '.');
    const value = parseFloat(normalized);
    return Number.isNaN(value) ? 0 : value;
  }

  function getRowTotal(row) {
    const quantityInput = row.querySelector('input[name$="-quantity"], #id_quantity');
    const priceInput = row.querySelector('input[name$="-price"], #id_price');
    return normalizeDecimal(quantityInput ? quantityInput.value : '0') * normalizeDecimal(priceInput ? priceInput.value : '0');
  }

  function applyStateToRow(row) {
    const statusSelect = row.querySelector('select[name$="-payment_status"], #id_payment_status');
    const paidAmountInput = row.querySelector('input[name$="-paid_amount"], #id_paid_amount');

    if (!statusSelect || !paidAmountInput) {
      return;
    }

    const isPartial = statusSelect.value === 'partial';
    const total = getRowTotal(row);
    const inputWrapper =
      paidAmountInput.closest('td') ||
      paidAmountInput.closest('.form-row, .field-box, div') ||
      paidAmountInput;

    paidAmountInput.readOnly = !isPartial;
    paidAmountInput.required = isPartial;
    inputWrapper.style.display = isPartial ? '' : 'none';

    if (!isPartial) {
      paidAmountInput.value = '0';
      paidAmountInput.removeAttribute('min');
      paidAmountInput.removeAttribute('max');
      return;
    }

    paidAmountInput.setAttribute('min', '0.01');
    if (total > 0) {
      paidAmountInput.setAttribute('max', total.toFixed(2));
    } else {
      paidAmountInput.removeAttribute('max');
    }
  }

  function updateInlinePaidAmountColumnVisibility(root) {
    const tables = root.querySelectorAll('table');

    tables.forEach(function (table) {
      const cells = table.querySelectorAll('td.field-paid_amount');
      if (cells.length === 0) return;

      let header = table.querySelector('th.column-paid_amount');
      if (!header) {
        const firstCell = cells[0];
        if (firstCell && Number.isInteger(firstCell.cellIndex)) {
          header = table.querySelector(`thead th:nth-child(${firstCell.cellIndex + 1})`);
        }
      }

      const statusSelects = table.querySelectorAll('select[name$="-payment_status"]');
      if (statusSelects.length === 0) {
        return;
      }

      const hasPartial = Array.from(statusSelects).some(function (select) {
        const row = select.closest('tr');
        if (!row || row.classList.contains('empty-form')) return false;

        const deleteCheckbox = row.querySelector('input[name$="-DELETE"]');
        if (deleteCheckbox && deleteCheckbox.checked) return false;

        return select.value === 'partial';
      });

      const displayValue = hasPartial ? '' : 'none';
      if (header) {
        header.style.setProperty('display', displayValue, 'important');
      }
      cells.forEach(function (cell) {
        cell.style.setProperty('display', displayValue, 'important');
      });
    });
  }

  function applyAllRows(root) {
    const inlineRows = root.querySelectorAll('tr.form-row, tr.dynamic-fooditem_set, tr.dynamic-rawitem_set, .inline-related tr');
    if (inlineRows.length > 0) {
      inlineRows.forEach(applyStateToRow);
      updateInlinePaidAmountColumnVisibility(root);
      return;
    }

    const standaloneForm = document.querySelector('form');
    if (standaloneForm) {
      applyStateToRow(standaloneForm);
    }

    updateInlinePaidAmountColumnVisibility(root);
  }

  function setupListeners(root) {
    root.addEventListener('change', function (event) {
      const target = event.target;
      if (!target) return;

      if (target.matches('select[name$="-payment_status"], #id_payment_status')) {
        const row = target.closest('tr') || document.querySelector('form');
        if (row) applyStateToRow(row);
        updateInlinePaidAmountColumnVisibility(root);
      }
    });

    root.addEventListener('input', function (event) {
      const target = event.target;
      if (!target) return;

      if (target.matches('input[name$="-quantity"], #id_quantity, input[name$="-price"], #id_price')) {
        const row = target.closest('tr') || document.querySelector('form');
        if (row) applyStateToRow(row);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    const root = document.body;
    applyAllRows(root);
    setupListeners(root);

    const observer = new MutationObserver(function () {
      applyAllRows(root);
    });

    observer.observe(root, { childList: true, subtree: true });
  });
})();
