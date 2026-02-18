// static/js/hisob.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('1. DOM yuklandi');

    // Barcha total maydonlarini boshlang'ich holatda readonly qilish
    function makeAllTotalFieldsReadonly() {
        // Standalone form total field
        const standaloneTotal = document.querySelector('#id_total, input[name="total"]');
        if (standaloneTotal) {
            standaloneTotal.readOnly = true;
        }

        // Inline qatorlardagi total maydonlar
        const allTotalInputs = document.querySelectorAll('input[name*="-total"]');
        allTotalInputs.forEach(input => {
            input.readOnly = true;
        });

        // Sale formdagi total_price maydoni
        const totalPriceField = document.querySelector('#id_total_price, input[name="total_price"]');
        if (totalPriceField) {
            totalPriceField.readOnly = true;
        }
    }

    makeAllTotalFieldsReadonly();

    function updateTotalPrice() {
        // Barcha inline qatorlardagi total larni yig'ish
        const inlineRows1 = document.querySelectorAll('.dynamic-saleitem_set tbody tr');
        const inlineRows2 = document.querySelectorAll('.inline-related tbody tr');
        const inlineRows3 = document.querySelectorAll('tr.dynamic-saleitem_set');
        const allRows = document.querySelectorAll('tbody tr');

        const inlineRows = inlineRows1.length > 0 ? inlineRows1 :
                         inlineRows2.length > 0 ? inlineRows2 :
                         inlineRows3.length > 0 ? inlineRows3 : allRows;

        let grandTotal = 0;

        inlineRows.forEach(function(row, index) {
            const totalInput = row.querySelector('input[name*="-total"]');
            if (totalInput && totalInput.value) {
                // Clean formatted value before parsing
                const totalStr = totalInput.value.replace(/\s+/g, '').replace(/,/g, '.');
                const totalValue = parseFloat(totalStr) || 0;
                grandTotal += totalValue;
                console.log(`Row ${index} total:`, totalValue, 'Grand total:', grandTotal);
            }
        });

        // Total price maydonini yangilash
        const totalPriceField = document.querySelector('#id_total_price, input[name="total_price"]');
        if (totalPriceField) {
            totalPriceField.value = grandTotal.toFixed(2);
            totalPriceField.readOnly = true; // Make it readonly
            // Trigger formatting for the total price field
            totalPriceField.dispatchEvent(new Event('input'));
            console.log('Total price updated:', grandTotal.toFixed(2));
        } else {
            console.log('Total price field not found');
        }
    }

    // Standalone form uchun
    const quantity = document.querySelector('#id_quantity, input[name="quantity"]');
    const price = document.querySelector('#id_price, input[name="price"]');

    console.log('3. Quantity:', quantity);
    console.log('4. Price:', price);

    if (quantity && price) {
        console.log('5. Inputlar topildi!');

        function hisobla() {
            // Clean formatted values before parsing
            const qStr = quantity.value.replace(/\s+/g, '').replace(/,/g, '.');
            const pStr = price.value.replace(/\s+/g, '').replace(/,/g, '.');
            const q = parseFloat(qStr) || 0;
            const p = parseFloat(pStr) || 0;
            const natija = (q * p).toFixed(2);
            console.log('6. Qiymatlar:', q, p, 'Natija:', natija);

            // Total maydonini yangilash
            const total = document.querySelector('#id_total, input[name="total"]');
            if (total) {
                total.value = natija;
                total.readOnly = true; // Make it readonly
                // Trigger formatting for the total field
                total.dispatchEvent(new Event('input'));
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
                    // Clean formatted values before parsing
                    const qStr = quantityInput.value.replace(/\s+/g, '').replace(/,/g, '.');
                    const pStr = priceInput.value.replace(/\s+/g, '').replace(/,/g, '.');
                    const q = parseFloat(qStr) || 0;
                    const p = parseFloat(pStr) || 0;
                    const natija = (q * p).toFixed(2);
                    totalInput.value = natija;
                    totalInput.readOnly = true; // Make it readonly
                    console.log(`Inline ${index} total updated:`, natija);

                    // Trigger formatting for the total field
                    totalInput.dispatchEvent(new Event('input'));

                    // Total price ni ham yangilash
                    updateTotalPrice();
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

        // Dastlabki total price ni hisoblash
        updateTotalPrice();
    }

    // Dastlabki qatorlarni sozlash
    setupInlineRows();

    // Dinamik qo'shiladigan qatorlar uchun kuzatuv
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    // Yangi qatorlarni tekshirish
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Agar yangi qator qo'shilgan bo'lsa
                        if (node.classList && node.classList.contains('dynamic-saleitem_set')) {
                            console.log('New saleitem_set detected');
                            setupInlineRows();
                        }
                        // Agar yangi tbody qo'shilgan bo'lsa
                        else if (node.tagName === 'TBODY') {
                            console.log('New tbody detected');
                            setupInlineRows();
                        }
                        // Agar yangi tr qo'shilgan bo'lsa
                        else if (node.tagName === 'TR' && node.querySelector('input[name*="-quantity"]')) {
                            console.log('New row detected');
                            setupInlineRows();
                        }
                        // Agar container ichida yangi qatorlar bo'lsa
                        else {
                            const rows = node.querySelectorAll ? node.querySelectorAll('tr') : [];
                            if (rows.length > 0) {
                                console.log('New container with rows detected');
                                setupInlineRows();
                            }
                        }
                    }
                });
            }
        });
    });

    const formContainer = document.querySelector('div[id*="saleitem_set-group"]') || document.querySelector('.inline-group') || document.body;
    if (formContainer) {
        console.log('Observing container:', formContainer);
        observer.observe(formContainer, {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false
        });
    }
});