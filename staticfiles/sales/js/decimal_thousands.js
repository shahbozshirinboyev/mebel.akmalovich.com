(function(){
  function cleanRaw(val){
    if(val === null || val === undefined) return '';
    return String(val).replace(/\s+/g, '').replace(/,/g, '.');
  }

  const MAX_DECIMALS = 2;

  function formatFromRaw(raw){
    if(!raw) return '';
    // split integer and decimal (allow only first dot)
    const parts = raw.split('.');
    const intRaw = parts[0] || '';
    let decRaw = parts.length > 1 ? parts.slice(1).join('') : '';
    const hasTrailingDot = raw.endsWith('.');
    // limit decimals to MAX_DECIMALS
    decRaw = decRaw.slice(0, MAX_DECIMALS);

    // remove leading zeros except keep single zero
    const intPart = (intRaw.replace(/^0+(?=\d)/, '') || '0')
      .replace(/\B(?=(\d{3})+(?!\d))/g, ' ');

    if(hasTrailingDot) return intPart + '.';
    return decRaw ? intPart + '.' + decRaw : intPart;
  }

  function setCaretByRawPosition(el, rawPos){
    // rawPos = number of non-space characters before caret in raw string
    const val = el.value;
    let count = 0;
    for(let i=0;i<val.length;i++){
      if(val[i] !== ' ') count++;
      if(count >= rawPos){
        // place caret after this char
        try{ el.setSelectionRange(i+1, i+1); }catch(err){}
        return;
      }
    }
    try{ el.setSelectionRange(val.length, val.length); }catch(err){}
  }

  function onInput(e){
    const el = e.target;
    const selStart = el.selectionStart || 0;
    // count non-space chars before caret to map after formatting
    const rawBefore = cleanRaw(el.value.slice(0, selStart));
    const nonSpaceBeforeCount = rawBefore.replace(/\s+/g,'').length;

    const raw = cleanRaw(el.value);
    // ensure only one dot exists
    const firstDotIndex = raw.indexOf('.');
    let normalized = raw;
    if(firstDotIndex !== -1){
      normalized = raw.slice(0, firstDotIndex+1) + raw.slice(firstDotIndex+1).replace(/\./g, '');
      // truncate any extra decimal digits beyond MAX_DECIMALS
      const dotIdx = normalized.indexOf('.');
      if(dotIdx !== -1){
        normalized = normalized.slice(0, dotIdx+1) + normalized.slice(dotIdx+1).slice(0, MAX_DECIMALS);
      }
    }

    const formatted = formatFromRaw(normalized);
    el.value = formatted;

    // restore caret position based on count of non-space chars
    setCaretByRawPosition(el, nonSpaceBeforeCount);
  }

  function stripSeparatorsBeforeSubmit(form){
    form.querySelectorAll('.thousand-sep').forEach(function(inp){
      if(inp.value) {
        const cleanValue = cleanRaw(inp.value).replace(/\s+/g, '');
        inp.value = cleanValue;
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    const all = Array.from(document.querySelectorAll('.thousand-sep'));

    function isNumericLikeInput(el){
      if(!el || el.tagName !== 'INPUT') return false;
      const t = (el.type || '').toLowerCase();
      // only target text-like inputs (avoid date/time, datetime-local, number, etc.)
      if(!['text','search','tel'].includes(t)) return false;

      // Check if input has thousand-sep class or looks numeric
      const hasThousandClass = el.classList.contains('thousand-sep');
      const v = el.value || '';
      const looksNumeric = v === '' || /^[0-9\s.,]*$/.test(v);

      return hasThousandClass || looksNumeric;
    }

    function setupThousandSeparator(inputs) {
      inputs.forEach(function(i){
        // Add thousand-sep class if not present
        if (!i.classList.contains('thousand-sep')) {
          i.classList.add('thousand-sep');
        }

        // Remove existing listeners to avoid duplicates
        i.removeEventListener('input', onInput);

        // initialize formatted value
        i.value = formatFromRaw(cleanRaw(i.value));
        i.addEventListener('input', onInput);
        // also format on blur
        i.addEventListener('blur', function(e){ e.target.value = formatFromRaw(cleanRaw(e.target.value)); });
      });
    }

    const inputs = all.filter(isNumericLikeInput);
    setupThousandSeparator(inputs);

    // strip separators on any admin form submit
    Array.from(document.querySelectorAll('form')).forEach(function(f){
      f.addEventListener('submit', function(){ stripSeparatorsBeforeSubmit(f); });
    });

    // Watch for dynamically added rows and apply thousand separator
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.addedNodes.length) {
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === Node.ELEMENT_NODE) {
              // Find all numeric inputs in the new node
              const newInputs = node.querySelectorAll ? node.querySelectorAll('input') : [];
              const numericInputs = Array.from(newInputs).filter(isNumericLikeInput);

              if (numericInputs.length > 0) {
                console.log('Found new numeric inputs:', numericInputs.length);
                setupThousandSeparator(numericInputs);
              }

              // Also check if the node itself is an input
              if (node.tagName === 'INPUT' && isNumericLikeInput(node)) {
                setupThousandSeparator([node]);
              }
            }
          });
        }
      });
    });

    // Start observing the entire document for changes
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: false,
      characterData: false
    });
  });
})();
