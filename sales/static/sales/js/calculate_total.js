document.addEventListener('DOMContentLoaded', function() {
    // Find all SaleItem inline rows
    const inlineRows = document.querySelectorAll('.dynamic-saleitem_set tbody tr');

    function setupTotalCalculation(row) {
        const quantityInput = row.querySelector('input[name*="-quantity"]');
        const priceInput = row.querySelector('input[name*="-price"]');

        // Find the total cell - it should be in the same row
        const cells = row.querySelectorAll('td');
        let totalCell = null;

        // Get the total cell (should be one of the cells in the row)
        cells.forEach(cell => {
            if (cell.textContent.includes('0.00') || cell.textContent.trim() === '' || !cell.querySelector('input')) {
                // This might be the read-only total cell
                if (row.cells.length > 0) {
                    // Find by position - total should be after price
                    const inputs = row.querySelectorAll('input[name*="-"]');
                    if (inputs.length >= 2) {
                        // Skip first inputs (product, quantity, price) and find the total cell
                        const cellIndex = Array.from(row.cells).length - 2; // Second to last cell before buyer
                        if (cellIndex >= 0 && cellIndex < row.cells.length) {
                            totalCell = row.cells[cellIndex];
                        }
                    }
                }
            }
        });

        if (!quantityInput || !priceInput) {
            return;
        }

        // Find total cell more reliably - look for a cell without input after price
        const allInputs = row.querySelectorAll('input, select');
        let foundPrice = false;
        for (let i = 0; i < row.cells.length; i++) {
            const cell = row.cells[i];
            const hasInput = cell.querySelector('input') || cell.querySelector('select');

            // After we find the cell with price input, skip buyer select and find the text cell
            if (cell === priceInput.closest('td')) {
                foundPrice = true;
            } else if (foundPrice && !hasInput) {
                totalCell = cell;
                break;
            }
        }

        if (!totalCell) {
            // Fallback: just use the first cell without input after price
            totalCell = row.cells[row.cells.length - 2];
        }

        function updateTotal() {
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const total = (quantity * price).toFixed(2);
            if (totalCell) {
                totalCell.textContent = total;
            }
        }

        // Trigger calculation on input
        quantityInput.addEventListener('input', updateTotal);
        quantityInput.addEventListener('change', updateTotal);
        priceInput.addEventListener('input', updateTotal);
        priceInput.addEventListener('change', updateTotal);

        // Initial calculation
        updateTotal();
    }

    // Setup for existing rows
    inlineRows.forEach(setupTotalCalculation);

    // Setup for dynamically added rows using MutationObserver
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.querySelectorAll) {
                        const newRows = node.querySelectorAll('.dynamic-saleitem_set tbody tr');
                        newRows.forEach(setupTotalCalculation);
                    }
                });
            }
        });
    });

    // Observe the inline form container for new rows
    const formContainer = document.querySelector('div[id*="saleitem_set-group"]') || document.querySelector('.inline-group');
    if (formContainer) {
        observer.observe(formContainer, { childList: true, subtree: true });
    }
});
