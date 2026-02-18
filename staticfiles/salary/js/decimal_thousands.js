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
      if(inp.value) inp.value = cleanRaw(inp.value).replace(/\s+/g, '');
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    const all = Array.from(document.querySelectorAll('.thousand-sep'));

    function isNumericLikeInput(el){
      if(!el || el.tagName !== 'INPUT') return false;
      const t = (el.type || '').toLowerCase();
      // only target text-like inputs (avoid date/time, datetime-local, number, etc.)
      if(!['text','search','tel'].includes(t)) return false;
      // allow if current value looks numeric (digits, spaces, dots, commas) or empty
      const v = el.value || '';
      return v === '' || /^[0-9\s.,]*$/.test(v);
    }

    const inputs = all.filter(isNumericLikeInput);
    inputs.forEach(function(i){
      // initialize formatted value
      i.value = formatFromRaw(cleanRaw(i.value));
      i.addEventListener('input', onInput);
      // also format on blur
      i.addEventListener('blur', function(e){ e.target.value = formatFromRaw(cleanRaw(e.target.value)); });
    });

    // strip separators on any admin form submit
    Array.from(document.querySelectorAll('form')).forEach(function(f){
      f.addEventListener('submit', function(){ stripSeparatorsBeforeSubmit(f); });
    });
  });
})();
