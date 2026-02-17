(function($) {
    $(document).ready(function() {
        function calculateTotal() {
            var quantity = parseFloat($('input[name="quantity"]').val()) || 0;
            var price = parseFloat($('input[name="price"]').val()) || 0;
            var total = quantity * price;

            // Format with thousand separator
            var formattedTotal = total.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });

            console.log('Calculating:', quantity, 'x', price, '=', total);

            // Update all possible total displays
            $('.total-item-price-display').text(formattedTotal);
            $('.field-total_item_price .readonly').text(formattedTotal);
            $('#id_total_item_price').closest('.form-row').find('.readonly').text(formattedTotal);

            // For inline forms
            var overallTotal = 0;
            $('.inline-group tr').each(function() {
                var row = this;
                var qty = parseFloat($(row).find('input[name*="quantity"]').val()) || 0;
                var prc = parseFloat($(row).find('input[name*="price"]').val()) || 0;
                var rowTotal = qty * prc;
                overallTotal += rowTotal;
                var formattedRowTotal = rowTotal.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
                $(row).find('.total-item-price-display').text(formattedRowTotal);
                $(row).find('td.field-total_item_price_display').text(formattedRowTotal);
            });

            // Update overall total cost
            var formattedOverallTotal = overallTotal.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            $('.field-total_cost .readonly').text(formattedOverallTotal);
        }

        // Setup event listeners
        $(document).on('input change', 'input[name*="quantity"], input[name*="price"]', function() {
            calculateTotal();
        });

        // Initial calculation
        calculateTotal();

        // Handle inline additions
        $('.add-row a').click(function() {
            setTimeout(calculateTotal, 100);
        });

        $(document).on('formset:added', function() {
            setTimeout(calculateTotal, 100);
        });
    });
})(django.jQuery || jQuery);
