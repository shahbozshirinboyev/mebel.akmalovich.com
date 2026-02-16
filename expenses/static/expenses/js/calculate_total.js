(function($) {
    $(document).ready(function() {
        function calculateTotal(row) {
            var quantity = parseFloat($(row).find('input[name*="quantity"]').val()) || 0;
            var price = parseFloat($(row).find('input[name*="price"]').val()) || 0;
            var total = quantity * price;

            // Format with thousand separator
            var formattedTotal = total.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            // Update the total display - try both span and td
            var totalDisplay = $(row).find('.total-item-price-display');
            if (totalDisplay.length === 0) {
                totalDisplay = $(row).find('td.field-total_item_price_display');
            }
            totalDisplay.text(formattedTotal);
        }

        // Function to add calculation to all rows
        function setupCalculationForAllRows() {
            $('.inline-group tr').each(function() {
                var row = this;

                // Only process rows that have quantity and price inputs
                if ($(row).find('input[name*="quantity"], input[name*="price"]').length > 0) {
                    // Setup event listeners
                    $(row).find('input[name*="quantity"], input[name*="price"]').on('input change', function() {
                        calculateTotal(row);
                    });

                    // Initial calculation
                    calculateTotal(row);
                }
            });
        }

        // Initial setup
        setupCalculationForAllRows();

        // Handle Django's inline form additions
        $(document).on('formset:added', function(event, row, formsetName) {
            setTimeout(function() {
                setupCalculationForAllRows();
            }, 100);
        });

        // Alternative for Django inline additions
        $('.add-row a').click(function() {
            setTimeout(function() {
                setupCalculationForAllRows();
            }, 100);
        });

        // Also handle tabular inline additions
        $('.inline-group').on('click', '.add-row a', function() {
            setTimeout(function() {
                setupCalculationForAllRows();
            }, 100);
        });
    });
})(django.jQuery || jQuery);
