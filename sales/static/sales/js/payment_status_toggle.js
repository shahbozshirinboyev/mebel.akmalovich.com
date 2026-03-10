(function () {
  function normalizeDecimal(raw) {
    if (!raw) return 0;
    const normalized = String(raw).replace(/\s+/g, '').replace(/,/g, '.');
    const value = parseFloat(normalized);
    return Number.isNaN(value) ? 0 : value;
  }

  function applyStateToRow(row) {
    const statusSelect = row.querySelector('select[name$="-payment_status"], #id_payment_status');
    const buyersPaidInput = row.querySelector('input[name$="-buyers_paid"], #id_buyers_paid');
    const totalInput = row.querySelector('input[name$="-total"], #id_total');

    if (!statusSelect || !buyersPaidInput) {
      return;
    }

    const isPartial = statusSelect.value === 'partial';
    const total = normalizeDecimal(totalInput ? totalInput.value : '0');
    const inputWrapper =
      buyersPaidInput.closest('td') ||
      buyersPaidInput.closest('.form-row, .field-box, div') ||
      buyersPaidInput;

    buyersPaidInput.readOnly = !isPartial;
    buyersPaidInput.required = isPartial;
    inputWrapper.style.display = isPartial ? '' : 'none';

    if (!isPartial) {
      buyersPaidInput.value = '0';
      buyersPaidInput.removeAttribute('min');
      buyersPaidInput.removeAttribute('max');
      return;
    }

    buyersPaidInput.setAttribute('min', '0.01');
    if (total > 0) {
      buyersPaidInput.setAttribute('max', total.toFixed(2));
    } else {
      buyersPaidInput.removeAttribute('max');
    }
  }

  function updateInlineBuyersPaidColumnVisibility(root) {
    const tables = root.querySelectorAll('table');

    tables.forEach(function (table) {
      const cells = table.querySelectorAll('td.field-buyers_paid');
      if (cells.length === 0) return;

      let header = table.querySelector('th.column-buyers_paid');
      if (!header) {
        const firstCell = cells[0];
        if (firstCell && Number.isInteger(firstCell.cellIndex)) {
          header = table.querySelector(`thead th:nth-child(${firstCell.cellIndex + 1})`);
        }
      }

      const statusSelects = table.querySelectorAll('select[name$="-payment_status"]');
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
    const inlineRows = root.querySelectorAll('tr.form-row, tr.dynamic-saleitem_set, .inline-related tr');
    if (inlineRows.length > 0) {
      inlineRows.forEach(applyStateToRow);
      updateInlineBuyersPaidColumnVisibility(root);
      return;
    }

    const standaloneForm = document.querySelector('form');
    if (standaloneForm) {
      applyStateToRow(standaloneForm);
    }

    updateInlineBuyersPaidColumnVisibility(root);
  }

  function setupListeners(root) {
    root.addEventListener('change', function (event) {
      const target = event.target;
      if (!target) return;

      if (target.matches('select[name$="-payment_status"], #id_payment_status')) {
        const row = target.closest('tr') || document.querySelector('form');
        if (row) applyStateToRow(row);
        updateInlineBuyersPaidColumnVisibility(root);
      }
    });

    root.addEventListener('input', function (event) {
      const target = event.target;
      if (!target) return;

      if (target.matches('input[name$="-total"], #id_total')) {
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
