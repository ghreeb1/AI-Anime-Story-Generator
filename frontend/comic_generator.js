document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('comic-form');
  const storyInput = document.getElementById('story');
  const styleSelect = document.getElementById('style');
  const panelsSection = document.getElementById('panels-section');
  const generateBtn = document.getElementById('generate-btn');
  const clearBtn = document.getElementById('clear-btn');

  // Detect text direction (RTL/LTR) based on input
  function detectDirection(text) {
    const rtlChars = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]/;
    return rtlChars.test(text) ? 'rtl' : 'ltr';
  }

  // Set page direction
  function setDirection(dir) {
    document.body.setAttribute('dir', dir);
  }

  // Download a single image as PNG
  function downloadImage(dataUrl, filename) {
    const a = document.createElement('a');
    a.href = dataUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Download all images as ZIP
  async function downloadAllAsZip(images) {
    if (!window.JSZip) {
      alert('JSZip library not loaded.');
      return;
    }
    const zip = new JSZip();
    images.forEach((img, idx) => {
      const base64 = img.b64.split(',')[1] || img.b64;
      zip.file(img.filename, base64ToUint8Array(base64));
    });
    const content = await zip.generateAsync({ type: 'blob' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(content);
    a.download = 'comic_panels.zip';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // Convert base64 to Uint8Array
  function base64ToUint8Array(base64) {
    const binary = atob(base64);
    const len = binary.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
  }

  // Render comic panels
  function renderPanels(images, dialoguesList, dir, readOnly = false) {
    panelsSection.innerHTML = '';
    setDirection(dir);
    generateBtn.disabled = false;
    images.forEach((img, idx) => {
      // Panel container
      const card = document.createElement('div');
      card.className = 'comic-panel-card';
      // Image container (for overlay)
      const imgContainer = document.createElement('div');
      imgContainer.className = 'image-container';
      imgContainer.style.width = '100%';
      imgContainer.style.position = 'relative';
      // Panel image
      const image = document.createElement('img');
      image.className = 'comic-panel-img';
      image.src = 'data:image/png;base64,' + img.b64;
      image.alt = `Panel ${idx+1}`;
      imgContainer.appendChild(image);
      // Speech bubble overlay
      const bubble = document.createElement('div');
      bubble.className = 'speech-bubble';
      bubble.setAttribute('tabindex', '0');
      // Compose bubble text from dialogues
      let bubbleText = '';
      if (Array.isArray(dialoguesList[idx])) {
        bubbleText = dialoguesList[idx].map(([speaker, line]) => speaker ? `${speaker}: ${line}` : line).join('\n');
      }
      bubble.innerText = bubbleText;
      // Set initial position (bottom center)
      bubble.style.left = '50%';
      bubble.style.top = '80%';
      bubble.style.transform = 'translate(-50%, 0)';
      // Bubble style state
      let bubbleStyle = 'default';
      // Drag state
      let isDragging = false, dragOffsetX = 0, dragOffsetY = 0;
      // Mouse events
      bubble.addEventListener('mousedown', function(e) {
        if (bubble.classList.contains('editing')) return;
        isDragging = true;
        bubble.classList.add('dragging');
        const rect = bubble.getBoundingClientRect();
        dragOffsetX = e.clientX - rect.left;
        dragOffsetY = e.clientY - rect.top;
        document.body.style.userSelect = 'none';
      });
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
      function onMouseMove(e) {
        if (!isDragging) return;
        moveBubble(e.clientX, e.clientY);
      }
      function onMouseUp() {
        if (isDragging) {
          isDragging = false;
          bubble.classList.remove('dragging');
          document.body.style.userSelect = '';
        }
      }
      // Touch events
      bubble.addEventListener('touchstart', function(e) {
        if (bubble.classList.contains('editing')) return;
        isDragging = true;
        bubble.classList.add('dragging');
        const touch = e.touches[0];
        const rect = bubble.getBoundingClientRect();
        dragOffsetX = touch.clientX - rect.left;
        dragOffsetY = touch.clientY - rect.top;
        e.preventDefault();
      }, { passive: false });
      document.addEventListener('touchmove', onTouchMove, { passive: false });
      document.addEventListener('touchend', onTouchEnd);
      function onTouchMove(e) {
        if (!isDragging) return;
        const touch = e.touches[0];
        moveBubble(touch.clientX, touch.clientY);
        e.preventDefault();
      }
      function onTouchEnd() {
        if (isDragging) {
          isDragging = false;
          bubble.classList.remove('dragging');
        }
      }
      // Move bubble helper
      function moveBubble(clientX, clientY) {
        const containerRect = imgContainer.getBoundingClientRect();
        const bubbleRect = bubble.getBoundingClientRect();
        let x = clientX - containerRect.left - dragOffsetX;
        let y = clientY - containerRect.top - dragOffsetY;
        // Clamp within container
        x = Math.max(0, Math.min(x, containerRect.width - bubbleRect.width));
        y = Math.max(0, Math.min(y, containerRect.height - bubbleRect.height));
        bubble.style.left = x + 'px';
        bubble.style.top = y + 'px';
        bubble.style.transform = 'none';
      }
      // Input field for live editing
      const input = document.createElement('input');
      input.type = 'text';
      input.className = 'speech-input';
      input.value = bubbleText;
      input.placeholder = 'Type dialogue...';
      input.addEventListener('input', function() {
        bubble.innerText = input.value;
      });
      // Sync bubble edits back to input (if user edits bubble directly)
      bubble.addEventListener('input', function() {
        input.value = bubble.innerText;
      });
      // Make bubble editable on double click
      bubble.setAttribute('contenteditable', 'true');
      bubble.spellcheck = true;
      // Prevent drag when editing text
      bubble.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') bubble.blur();
      });
      bubble.addEventListener('focus', function() {
        bubble.classList.add('editing');
      });
      bubble.addEventListener('blur', function() {
        bubble.classList.remove('editing');
      });
      // Only allow drag if not focused for editing
      bubble.addEventListener('mousedown', function(e) {
        if (document.activeElement === bubble) {
          isDragging = false;
          return;
        }
      });
      // Bubble style selector
      const styleSelector = document.createElement('select');
      styleSelector.className = 'bubble-style-selector';
      [
        { value: 'default', label: 'Speech' },
        { value: 'thought', label: 'Thought' },
        { value: 'jagged', label: 'Shout' }
      ].forEach(opt => {
        const o = document.createElement('option');
        o.value = opt.value;
        o.innerText = opt.label;
        styleSelector.appendChild(o);
      });
      styleSelector.value = 'default';
      styleSelector.addEventListener('change', function() {
        bubble.classList.remove('thought', 'jagged');
        bubbleStyle = styleSelector.value;
        if (bubbleStyle === 'thought') bubble.classList.add('thought');
        else if (bubbleStyle === 'jagged') bubble.classList.add('jagged');
      });
      // Download with Bubble button
      const dlBubbleBtn = document.createElement('button');
      dlBubbleBtn.innerText = 'Download with Bubble';
      dlBubbleBtn.type = 'button';
      dlBubbleBtn.style.marginLeft = '8px';
      dlBubbleBtn.onclick = function() {
        exportPanelWithBubble(image, bubble, bubbleStyle, card);
      };
      // Assemble
      imgContainer.appendChild(bubble);
      card.appendChild(imgContainer);
      card.appendChild(input);
      card.appendChild(styleSelector);
      // Download buttons
      const actions = document.createElement('div');
      actions.className = 'panel-actions';
      // Download PNG
      const dlBtn = document.createElement('button');
      dlBtn.innerText = 'Download PNG';
      dlBtn.onclick = () => downloadImage(image.src, img.filename || `panel_${idx+1}.png`);
      actions.appendChild(dlBtn);
      actions.appendChild(dlBubbleBtn);
      card.appendChild(actions);
      panelsSection.appendChild(card);
      // If readOnly mode is requested, disable editable controls for this panel
      if (readOnly) {
        bubble.contentEditable = 'false';
        bubble.classList.add('readonly-bubble');
        bubble.style.pointerEvents = 'none';
        input.disabled = true;
        styleSelector.disabled = true;
      }
    });
    // Hook up the right-side download panel button instead of creating an in-panel button
    const downloadSideBtn = document.getElementById('download-zip-panel-btn');
    if (downloadSideBtn) {
      downloadSideBtn.onclick = () => downloadAllAsZip(images);
    }
    // If readOnly, mark the preview card as readonly (visually and behaviour)
    const previewCard = document.getElementById('preview-card');
    if (previewCard) {
      if (readOnly) previewCard.classList.add('readonly');
      else previewCard.classList.remove('readonly');
    }
  }

  // Export panel with bubble as PNG
  function exportPanelWithBubble(imageElem, bubbleElem, bubbleStyle, cardElem) {
    const img = new window.Image();
    img.src = imageElem.src;
    img.onload = function() {
      const imgW = img.width;
      const imgH = img.height;
      const scale = imgW / imageElem.offsetWidth;
      const canvas = document.createElement('canvas');
      canvas.width = imgW;
      canvas.height = imgH;
      const ctx = canvas.getContext('2d');
      // Draw base image
      ctx.drawImage(img, 0, 0, imgW, imgH);
      // Get bubble position and size relative to image
      const imgRect = imageElem.getBoundingClientRect();
      const bubbleRect = bubbleElem.getBoundingClientRect();
      const cardRect = cardElem.getBoundingClientRect();
      // Calculate bubble position relative to image
      const bx = (bubbleRect.left - imgRect.left) * scale;
      const by = (bubbleRect.top - imgRect.top) * scale;
      const bw = bubbleRect.width * scale;
      const bh = bubbleRect.height * scale;
      // Draw bubble shape
      ctx.save();
      ctx.font = `${Math.round(18 * scale)}px 'Comic Sans MS', 'Comic Neue', 'Comic Sans', cursive, sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      // Bubble background
      if (bubbleStyle === 'thought') {
        // Draw cloud shape
        drawThoughtCloud(ctx, bx, by, bw, bh);
      } else if (bubbleStyle === 'jagged') {
        // Draw jagged shape
        drawJaggedBubble(ctx, bx, by, bw, bh);
      } else {
        // Default rounded rect
        roundRect(ctx, bx, by, bw, bh, 32 * scale);
      }
      ctx.fillStyle = '#fff';
      ctx.globalAlpha = 0.98;
      ctx.fill();
      ctx.globalAlpha = 1.0;
      ctx.lineWidth = 4 * scale;
      ctx.strokeStyle = '#222';
      ctx.shadowColor = 'rgba(0,0,0,0.18)';
      ctx.shadowBlur = 8 * scale;
      ctx.stroke();
      ctx.shadowBlur = 0;
      // Bubble text
      ctx.fillStyle = '#222';
      ctx.font = `${Math.round(18 * scale)}px 'Comic Sans MS', 'Comic Neue', 'Comic Sans', cursive, sans-serif`;
      const lines = bubbleElem.innerText.split('\n');
      const lineHeight = 26 * scale;
      lines.forEach((line, i) => {
        ctx.fillText(line, bx + bw/2, by + bh/2 + (i - (lines.length-1)/2) * lineHeight);
      });
      ctx.restore();
      // Download
      const dataUrl = canvas.toDataURL('image/png');
      downloadImage(dataUrl, 'panel_with_bubble.png');
    };
  }
  // Helper: rounded rect
  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }
  // Helper: thought cloud
  function drawThoughtCloud(ctx, x, y, w, h) {
    ctx.beginPath();
    const steps = 6;
    const rBig = Math.min(w, h) / 2.2;
    const rSmall = rBig / 2.5;
    const cx = x + w/2, cy = y + h/2;
    for (let i = 0; i < steps; i++) {
      const angle = (Math.PI * 2 / steps) * i;
      const r = i % 2 === 0 ? rBig : rSmall;
      ctx.arc(cx + Math.cos(angle) * rBig * 0.7, cy + Math.sin(angle) * rBig * 0.7, r, 0, Math.PI * 2);
    }
    ctx.closePath();
  }
  // Helper: jagged bubble
  function drawJaggedBubble(ctx, x, y, w, h) {
    ctx.beginPath();
    const spikes = 16;
    const cx = x + w/2, cy = y + h/2;
    const outerR = Math.min(w, h) / 2;
    const innerR = outerR * 0.8;
    for (let i = 0; i < spikes; i++) {
      const angle = (Math.PI * 2 / spikes) * i;
      const r = i % 2 === 0 ? outerR : innerR;
      ctx.lineTo(cx + Math.cos(angle) * r, cy + Math.sin(angle) * r);
    }
    ctx.closePath();
  }

  // Handle form submission
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    const story = storyInput.value.trim();
    const style = styleSelect.value;
    const negative_prompt = negativePromptInput && negativePromptInput.value ? negativePromptInput.value.trim() : '';
    // Read optional generation controls (if present)
    const widthInput = document.getElementById('gen-width');
    const heightInput = document.getElementById('gen-height');
    const stepsInput = document.getElementById('gen-steps');
    const guidanceInput = document.getElementById('gen-guidance');
    const genParams = {};
    if (widthInput && widthInput.value) genParams.width = parseInt(widthInput.value, 10);
    if (heightInput && heightInput.value) genParams.height = parseInt(heightInput.value, 10);
    if (stepsInput && stepsInput.value) genParams.steps = parseInt(stepsInput.value, 10);
    if (guidanceInput && guidanceInput.value) genParams.guidance_scale = parseFloat(guidanceInput.value);
    if (!story) return;
    const dir = detectDirection(story);
    setDirection(dir);
    panelsSection.innerHTML = '<div class="loading" style="text-align:center;padding:32px;">\n      <svg width="48" height="48" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:8px;">\n        <circle cx="25" cy="25" r="20" stroke="rgba(124,58,237,0.25)" stroke-width="5" fill="none" stroke-linecap="round"></circle>\n      </svg>\n      <div style="color:rgba(255,255,255,0.8);">Generating panels This may take a moment...</div>\n    </div>';
    generateBtn.disabled = true;
    try {
      const body = { story, style, negative_prompt };
      // Attach generation params so backend can apply them to each prompt
      if (Object.keys(genParams).length) body.generation = genParams;
      // Include overlay_bubbles=false so backend doesn't render bubbles into images
      body.overlay_bubbles = false;
      const resp = await fetch('/generate/comic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!resp.ok) throw new Error('Failed to generate comic');
      const data = await resp.json();
      const images = data.images || [];
      const dialoguesList = data.dialogues || images.map(() => []);
      // After generating, render panels and allow client-side editing of bubbles
      // Also send overlay_bubbles=false in the request so server doesn't bake bubbles into PNGs
      renderPanels(images, dialoguesList, dir, false);
    } catch (err) {
      panelsSection.innerHTML = '<div style="color:#ffb4b4;text-align:center;padding:32px;">Error: ' + err.message + '</div>';
      generateBtn.disabled = false;
    }
  });

  // Load JSZip for ZIP downloads
  const jszipScript = document.createElement('script');
  jszipScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
  document.body.appendChild(jszipScript);

  const negativePromptInput = document.createElement('input');
  negativePromptInput.type = 'text';
  negativePromptInput.id = 'negative-prompt';
  negativePromptInput.placeholder = 'Negative prompt (optional: e.g. text, watermark, blurry, ... )';
  negativePromptInput.style = 'width: 100%; margin-bottom: 12px;';
  form.insertBefore(negativePromptInput, panelsSection);

  // Clear form action
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      storyInput.value = '';
      negativePromptInput.value = '';
      panelsSection.innerHTML = '';
      generateBtn.disabled = false;
    });
  }
});
