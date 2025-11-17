function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  const itemEl = ev.currentTarget || ev.target.closest('.item');
  if (!itemEl) return;

  // Keep the same key drop() reads
  ev.dataTransfer.setData("text", itemEl.id);
  ev.dataTransfer.setData("source", itemEl.dataset.source);
  ev.dataTransfer.effectAllowed = "copyMove";

  const img = itemEl.querySelector('img');
  if (!img) return;

  // ***This (if condition) is how we can apply properties to the items in the grid without changing how the original items in the items-box work
  // Don't make images in the source items-box (data-source="list") transparent.
  if (itemEl.dataset.source !== 'list') {
    itemEl.style.opacity = '0';
  }
  /* Could also do: itemEl.style.visibility = 'hidden';*/

  // Use the rendered size so the drag image matches what the user sees
  const rect = img.getBoundingClientRect();
  const w = Math.max(1, Math.round(rect.width || img.width || 75));
  const h = Math.max(1, Math.round(rect.height || img.height || 75));

  // Clone the <img>, place it offscreen (not display:none), and use it as the drag image.
  // Many browsers require the element to be in the DOM to render as a drag image.
  const clone = img.cloneNode(true);
  clone.style.position = 'absolute';
  clone.style.top = '-9999px';
  clone.style.left = '-9999px';
  clone.style.width = w + 'px';
  clone.style.height = h + 'px';
  clone.style.pointerEvents = 'none';
  // Ensure it's fully visible/opaque for the drag image
  clone.style.opacity = '1';
  document.body.appendChild(clone);

  // center pointer on the sprite
  ev.dataTransfer.setDragImage(clone, Math.floor(w / 2), Math.floor(h / 2));

  // Cleanup: remove clone when drag ends (works across browsers). Use document for robustness.
  const cleanup = () => {
    if (clone && clone.parentNode) {
      clone.parentNode.removeChild(clone);
      /* Need this for dragging from one part of the grid to another */
      itemEl.style.opacity = '1';
    }
    document.removeEventListener('dragend', cleanup);
    // Also remove touchcancel if needed (some platforms)
    document.removeEventListener('touchend', cleanup);
  };
  document.addEventListener('dragend', cleanup, { once: true });
  document.addEventListener('touchend', cleanup, { once: true });
}

function drop(ev) {
  ev.preventDefault();
  const id = ev.dataTransfer.getData("text");
  const sourceType = ev.dataTransfer.getData("source");
  const original = document.getElementById(id);
  if (!original) return; // Safety check

  if (!ev.target.classList.contains('cell')) return;

  ev.target.innerHTML = '';
  let elementToAppend;

  if (sourceType === "list") {
    const clone = original.cloneNode(true);
    clone.id = original.id + "-" + Math.random().toString(36).substr(2, 5);
    clone.setAttribute("draggable", "true");
    clone.dataset.source = "grid";
    clone.ondragstart = drag;

    /* Need to have this for the first initial drag from the item-box */
    clone.style.opacity = '1';

    elementToAppend = clone;
  } else {
    elementToAppend = original;
  }

  ev.target.appendChild(elementToAppend);
  seeRecipe();
}

// Clears all items inside the grid
function clearGrid() {
  const cells = document.querySelectorAll('.grid .cell');
  cells.forEach(cell => {
    cell.innerHTML = '';
  });
  const outImg = document.getElementById("output-image");
  outImg.src = "";
  outImg.style.display = "none";
}

// Removes nulls from columns, preserves if null is between two items in a column
function trimNullColumns(grid) {
  if (!grid.length) return grid;

  const numCols = grid[0].length;
  let firstCol = numCols, lastCol = -1;

  for (let col = 0; col < numCols; col++) {
    const hasValue = grid.some(row => row[col] !== null);
    if (hasValue) {
      firstCol = Math.min(firstCol, col);
      lastCol = Math.max(lastCol, col);
    }
  }

  // If all columns are null, just return the original grid
  if (lastCol === -1) return grid;

  return grid.map(row => row.slice(firstCol, lastCol + 1));
}

// Removes nulls from rows, preserves if null is between two items in a row
function trimNullRows(grid) {
  const numRows = grid.length;
  let firstRow = numRows, lastRow = -1;

  for (let row = 0; row < numRows; row++) {
    const hasValue = grid[row].some(cell => cell !== null);
    if (hasValue) {
      firstRow = Math.min(firstRow, row);
      lastRow = Math.max(lastRow, row);
    }
  }

  // If all rows are null, just return the original grid
  if (lastRow === -1) return grid;

  return grid.slice(firstRow, lastRow + 1);
}

// Sends grid to backend to confirm if pattern in grid is an accepted recipe
// If recipe is valid, display image of craftable item in frontend
function seeRecipe() {
  const rawGrid = Array.from({ length: 3 }, () => Array(3).fill(null));

  // Going through grid, and filling out grid data array
  document.querySelectorAll('.cell').forEach(cell => {
    const row = cell.dataset.row;
    const col = cell.dataset.col;

    const item = cell.querySelector('.item');
    rawGrid[row][col] = item ? item.dataset.id : null;
  });
  // Calling functions to remove nulls
  let trimmedGrid = trimNullRows(rawGrid);
  trimmedGrid = trimNullColumns(trimmedGrid);

  // Send to server
  fetch('/submit-guess', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ grid: trimmedGrid })
  })
  .then(res => res.json())
  // Display craftable item
  .then(data => {
    console.log("SERVER RESPONSE:", data);
    if (data.success && data.crafted_item) {
      const img = document.getElementById("output-image");
      img.src = `/static/items/${data.crafted_item}.png`;
      img.style.display = "block";
    }
  })
  .catch(err => console.error('Error:', err));
}
function submitGrid() {
  seeRecipe();
  //We should be able add more logic down here when we want to change guess colors once they press the actual "Submit Guess" button
}