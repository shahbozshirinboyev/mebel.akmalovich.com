// static/js/hisob.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('1. DOM yuklandi');

    // Standalone form uchun
    const quantity = document.querySelector('#id_quantity, input[name="quantity"]');
    const price = document.querySelector('#id_price, input[name="price"]');

    console.log('3. Quantity:', quantity);
    console.log('4. Price:', price);

    if (quantity && price) {
        console.log('5. Inputlar topildi!');

        function hisobla() {
            const q = parseFloat(quantity.value) || 0;
            const p = parseFloat(price.value) || 0;
            const natija = (q * p).toFixed(2);
            console.log('6. Qiymatlar:', q, p, 'Natija:', natija);

            // Total maydonini yangilash
            const total = document.querySelector('#id_total, input[name="total"]');
            if (total) {
                total.value = natija;
                console.log('7. Total maydoni yangilandi:', natija);
            } else {
                console.error('Total maydoni topilmadi!');
            }
        }

        quantity.addEventListener('input', hisobla);
        price.addEventListener('input', hisobla);
    } else {
        console.log('Standalone form emas, inline qatorlarni qidiramiz...');
    }

    // Inline qatorlar uchun (Sale admin form)
    function setupInlineRows() {
        // Turli selektorlar bilan qatorlarni qidirish
        const inlineRows1 = document.querySelectorAll('.dynamic-saleitem_set tbody tr');
        const inlineRows2 = document.querySelectorAll('.inline-related tbody tr');
        const inlineRows3 = document.querySelectorAll('tr.dynamic-saleitem_set');
        const allRows = document.querySelectorAll('tbody tr');

        console.log('Inline rows qidiruv:', {
            '.dynamic-saleitem_set tbody tr': inlineRows1.length,
            '.inline-related tbody tr': inlineRows2.length,
            'tr.dynamic-saleitem_set': inlineRows3.length,
            'tbody tr': allRows.length
        });

        const inlineRows = inlineRows1.length > 0 ? inlineRows1 :
                         inlineRows2.length > 0 ? inlineRows2 :
                         inlineRows3.length > 0 ? inlineRows3 : allRows;

        console.log('Final inline rows found:', inlineRows.length);

        inlineRows.forEach(function(row, index) {
            const quantityInput = row.querySelector('input[name*="-quantity"]');
            const priceInput = row.querySelector('input[name*="-price"]');
            const totalInput = row.querySelector('input[name*="-total"]');

            console.log(`Row ${index}:`, {
                rowHTML: row.outerHTML.substring(0, 100) + '...',
                quantity: !!quantityInput,
                price: !!priceInput,
                total: !!totalInput,
                allInputs: row.querySelectorAll('input').length
            });

            if (quantityInput && priceInput && totalInput) {
                function updateInlineTotal() {
                    const q = parseFloat(quantityInput.value) || 0;
                    const p = parseFloat(priceInput.value) || 0;
                    const natija = (q * p).toFixed(2);
                    totalInput.value = natija;
                    console.log(`Inline ${index} total updated:`, natija);
                }

                quantityInput.addEventListener('input', updateInlineTotal);
                priceInput.addEventListener('input', updateInlineTotal);
                updateInlineTotal(); // Initial calculation
            } else {
                console.log(`Row ${index} inputs not found, checking all inputs:`);
                row.querySelectorAll('input').forEach((input, i) => {
                    console.log(`  Input ${i}:`, input.name, input.type, input.id);
                });
            }
        });
    }

    // Dastlabki qatorlarni sozlash
    setupInlineRows();

    // Dinamik qo'shiladigan qatorlar uchun kuzatuv
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.classList && node.classList.contains('dynamic-saleitem_set')) {
                        setupInlineRows();
                    }
                });
            }
        });
    });

    const formContainer = document.querySelector('div[id*="saleitem_set-group"]') || document.querySelector('.inline-group');
    if (formContainer) {
        observer.observe(formContainer, { childList: true, subtree: true });
    }
});