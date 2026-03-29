// salary/js/calculate_salary_total.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('1. Salary DOM yuklandi');

    // Debug: Barcha input larni ko'rsatish
    console.log('All inputs on page:', document.querySelectorAll('input'));
    console.log('All thousand-sep inputs:', document.querySelectorAll('.thousand-sep'));

    // Barcha total maydonlarini boshlang'ich holatda readonly qilish
    function makeAllTotalFieldsReadonly() {
        // Salary formdagi total_earned_salary maydoni
        const totalEarnedField = document.querySelector('#id_total_earned_salary, input[name="total_earned_salary"]');
        console.log('Total earned field found:', !!totalEarnedField, totalEarnedField);
        if (totalEarnedField) {
            totalEarnedField.readOnly = true;
            console.log('Total earned field made readonly, current value:', totalEarnedField.value);
        }

        // Salary formdagi total_paid_salary maydoni
        const totalPaidField = document.querySelector('#id_total_paid_salary, input[name="total_paid_salary"]');
        console.log('Total paid field found:', !!totalPaidField, totalPaidField);
        if (totalPaidField) {
            totalPaidField.readOnly = true;
            console.log('Total paid field made readonly, current value:', totalPaidField.value);
        }
    }

    // Boshlang'ich readonly qilishni keyinroq qilamiz, chunki avval hisoblash kerak

    function updateSalaryTotals() {
        console.log('Updating salary totals...');

        // Django admin inline form lari uchun to'g'ri selektorlar
        const inlineRows1 = document.querySelectorAll('.dynamic-salaryitem_set tbody tr');
        const inlineRows2 = document.querySelectorAll('.inline-related tbody tr');
        const inlineRows3 = document.querySelectorAll('tr.dynamic-salaryitem_set');
        const allRows = document.querySelectorAll('tbody tr');

        // Debug: qatorlarni ko'rsatish
        console.log('Inline rows found:', {
            '.dynamic-salaryitem_set tbody tr': inlineRows1.length,
            '.inline-related tbody tr': inlineRows2.length,
            'tr.dynamic-salaryitem_set': inlineRows3.length,
            'tbody tr': allRows.length
        });

        const inlineRows = inlineRows1.length > 0 ? inlineRows1 :
                         inlineRows2.length > 0 ? inlineRows2 :
                         inlineRows3.length > 0 ? inlineRows3 : allRows;

        console.log('Using inline rows:', inlineRows.length);

        let totalEarned = 0;
        let totalPaid = 0;

        inlineRows.forEach(function(row, index) {
            const earnedInput = row.querySelector('input[name*="-earned_amount"]');
            const paidInput = row.querySelector('input[name*="-paid_amount"]');

            console.log(`Row ${index}:`, {
                rowHTML: row.outerHTML.substring(0, 200) + '...',
                earnedInput: !!earnedInput,
                paidInput: !!paidInput,
                earnedValue: earnedInput ? earnedInput.value : 'N/A',
                paidValue: paidInput ? paidInput.value : 'N/A',
                allInputs: row.querySelectorAll('input').length
            });

            if (earnedInput && earnedInput.value) {
                // Clean formatted value before parsing
                const earnedStr = earnedInput.value.replace(/\s+/g, '').replace(/,/g, '.');
                const earnedValue = parseFloat(earnedStr) || 0;
                totalEarned += earnedValue;
                console.log(`Row ${index} earned:`, earnedValue, 'Total earned:', totalEarned);
            }

            if (paidInput && paidInput.value) {
                // Clean formatted value before parsing
                const paidStr = paidInput.value.replace(/\s+/g, '').replace(/,/g, '.');
                const paidValue = parseFloat(paidStr) || 0;
                totalPaid += paidValue;
                console.log(`Row ${index} paid:`, paidValue, 'Total paid:', totalPaid);
            }
        });

        console.log('Final totals - Earned:', totalEarned, 'Paid:', totalPaid);

        // Total maydonlarini yangilash
        const totalEarnedField = document.querySelector('#id_total_earned_salary, input[name="total_earned_salary"]');
        const totalPaidField = document.querySelector('#id_total_paid_salary, input[name="total_paid_salary"]');

        if (totalEarnedField) {
            // Avval readonly ni olib tashlaymiz
            const wasReadonly = totalEarnedField.readOnly;
            totalEarnedField.readOnly = false;
            
            // Qiymatni o'rnatamiz
            totalEarnedField.value = totalEarned.toFixed(2);
            console.log('Total earned field set to:', totalEarned.toFixed(2));
            
            // Trigger formatting for the total field
            totalEarnedField.dispatchEvent(new Event('input'));
            
            // Qayta readonly qilamiz
            totalEarnedField.readOnly = true;
            console.log('Total earned field updated and made readonly');
        } else {
            console.log('Total earned field not found');
        }

        if (totalPaidField) {
            // Avval readonly ni olib tashlaymiz
            const wasReadonly = totalPaidField.readOnly;
            totalPaidField.readOnly = false;
            
            // Qiymatni o'rnatamiz
            totalPaidField.value = totalPaid.toFixed(2);
            console.log('Total paid field set to:', totalPaid.toFixed(2));
            
            // Trigger formatting for the total field
            totalPaidField.dispatchEvent(new Event('input'));
            
            // Qayta readonly qilamiz
            totalPaidField.readOnly = true;
            console.log('Total paid field updated and made readonly');
        } else {
            console.log('Total paid field not found');
        }
        
        // Oxirida readonly qilish
        makeAllTotalFieldsReadonly();
    }

    // Dastlabki hisoblash
    updateSalaryTotals();

    // Inline qatorlardagi inputlarga event listener qo'shish
    function setupInlineRows() {
        console.log('Setting up inline rows...');

        const inlineRows1 = document.querySelectorAll('.dynamic-salaryitem_set tbody tr');
        const inlineRows2 = document.querySelectorAll('.inline-related tbody tr');
        const inlineRows3 = document.querySelectorAll('tr.dynamic-salaryitem_set');
        const allRows = document.querySelectorAll('tbody tr');

        const inlineRows = inlineRows1.length > 0 ? inlineRows1 :
                         inlineRows2.length > 0 ? inlineRows2 :
                         inlineRows3.length > 0 ? inlineRows3 : allRows;

        console.log('Setup inline rows found:', inlineRows.length);

        inlineRows.forEach(function(row, index) {
            const earnedInput = row.querySelector('input[name*="-earned_amount"]');
            const paidInput = row.querySelector('input[name*="-paid_amount"]');

            console.log(`Setting up row ${index}:`, {
                earnedInput: !!earnedInput,
                paidInput: !!paidInput
            });

            if (earnedInput) {
                earnedInput.addEventListener('input', updateSalaryTotals);
                console.log('Added listener to earned input');
            }

            if (paidInput) {
                paidInput.addEventListener('input', updateSalaryTotals);
                console.log('Added listener to paid input');
            }
        });
    }

    setupInlineRows();

    // Django admin delete tugmalarini kuzatish
    function setupDeleteListeners() {
        console.log('Setting up delete listeners');
        
        // Delete checkbox lar va delete tugmalarini kuzatish
        const deleteCheckboxes = document.querySelectorAll('input[name*="-DELETE"]');
        const deleteLinks = document.querySelectorAll('a.inline-deletelink');
        
        console.log('Found delete checkboxes:', deleteCheckboxes.length);
        console.log('Found delete links:', deleteLinks.length);
        
        // Delete checkbox lar uchun
        deleteCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                console.log('Delete checkbox changed:', checkbox.checked);
                setTimeout(function() {
                    updateSalaryTotals();
                }, 50);
            });
        });
        
        // Delete linklar uchun
        deleteLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                console.log('Delete link clicked');
                // Link bosilganda DOM o'zgarishini MutationObserver tutadi
                setTimeout(function() {
                    updateSalaryTotals();
                }, 100);
            });
        });
    }

    // Dastlabki delete listenerlarni o'rnatish
    setupDeleteListeners();

    // Dinamik qo'shiladigan va o'chiriladigan qatorlar uchun kuzatuv
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Agar yangi qator yoki container qo'shilgan bo'lsa
                        if (node.classList && node.classList.contains('dynamic-salaryitem_set')) {
                            console.log('New salaryitem_set detected');
                            setTimeout(function() {
                                makeAllTotalFieldsReadonly();
                                setupInlineRows();
                                setupDeleteListeners();
                                updateSalaryTotals();
                            }, 100);
                        }
                        else if (node.tagName === 'TBODY') {
                            console.log('New tbody detected');
                            setTimeout(function() {
                                makeAllTotalFieldsReadonly();
                                setupInlineRows();
                                setupDeleteListeners();
                                updateSalaryTotals();
                            }, 100);
                        }
                        else if (node.tagName === 'TR' && node.querySelector('input[name*="-earned_amount"]')) {
                            console.log('New salary row detected');
                            setTimeout(function() {
                                makeAllTotalFieldsReadonly();
                                setupInlineRows();
                                setupDeleteListeners();
                                updateSalaryTotals();
                            }, 100);
                        }
                        else {
                            const rows = node.querySelectorAll ? node.querySelectorAll('tr') : [];
                            if (rows.length > 0) {
                                console.log('New container with rows detected');
                                setTimeout(function() {
                                    makeAllTotalFieldsReadonly();
                                    setupInlineRows();
                                    updateSalaryTotals();
                                }, 100);
                            }
                        }
                    }
                });
            }
            
            // O'chirilgan qatorlarni kuzatish
            if (mutation.removedNodes.length) {
                mutation.removedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Agar qator o'chirilgan bo'lsa
                        if (node.tagName === 'TR' && node.querySelector('input[name*="-earned_amount"], input[name*="-paid_amount"]')) {
                            console.log('Salary row deleted, updating totals');
                            setTimeout(function() {
                                makeAllTotalFieldsReadonly();
                                setupInlineRows();
                                setupDeleteListeners();
                                updateSalaryTotals();
                            }, 100);
                        }
                        else if (node.classList && node.classList.contains('dynamic-salaryitem_set')) {
                            console.log('Salaryitem_set deleted, updating totals');
                            setTimeout(function() {
                                makeAllTotalFieldsReadonly();
                                setupInlineRows();
                                setupDeleteListeners();
                                updateSalaryTotals();
                            }, 100);
                        }
                    }
                });
            }
        });
    });

    const formContainer = document.querySelector('div[id*="salaryitem_set-group"]') || document.querySelector('.inline-group') || document.body;
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
