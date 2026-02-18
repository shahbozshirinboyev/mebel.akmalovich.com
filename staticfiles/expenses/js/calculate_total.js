(function($) {
    $(document).ready(function() {
        // Helper function to clean formatted numbers
        function cleanNumber(val) {
            if (!val) return 0;
            return parseFloat(val.toString().replace(/\s+/g, '').replace(/,/g, '.')) || 0;
        }

        // Helper function to format numbers like decimal_thousands.js
        function formatNumber(num) {
            if (!num && num !== 0) return '0.00';
            return num.toLocaleString('de-DE', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        }

        function calculateTotal() {
            // For single form (FoodItem or RawItem add)
            var quantity = cleanNumber($('input[name="quantity"]').val());
            var price = cleanNumber($('input[name="price"]').val());
            var total = quantity * price;
            var formattedTotal = formatNumber(total);
            $('.field-total_item_price .readonly').text(formattedTotal);
            $('#id_total_item_price').closest('.form-row').find('.readonly').text(formattedTotal);

            var foodTotal = 0;
            var rawTotal = 0;

            // Calculate for each inline group
            $('.inline-group').each(function(index, group) {
                var groupTotal = 0;
                $(group).find('tr').each(function() {
                    var row = this;
                    var qty = cleanNumber($(row).find('input[name*="quantity"]').val());
                    var prc = cleanNumber($(row).find('input[name*="price"]').val());
                    var rowTotal = qty * prc;
                    groupTotal += rowTotal;
                    var formattedRowTotal = formatNumber(rowTotal);
                    $(row).find('.total-item-price-display').text(formattedRowTotal);
                    $(row).find('td.field-total_item_price_display').text(formattedRowTotal);
                });

                if (index === 0) {
                    foodTotal = groupTotal;
                } else if (index === 1) {
                    rawTotal = groupTotal;
                }
            });

            var overallTotal = foodTotal + rawTotal;

            // Update food total
            var formattedFoodTotal = formatNumber(foodTotal);
            $('.field-food_items_total .readonly').text(formattedFoodTotal);

            // Update raw total
            var formattedRawTotal = formatNumber(rawTotal);
            $('.field-raw_items_total .readonly').text(formattedRawTotal);

            // Update overall total cost
            var formattedOverallTotal = formatNumber(overallTotal);
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
