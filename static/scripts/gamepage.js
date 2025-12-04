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

  // Making the crafting output disappear when you change what is in the crafting table
    // Reappears once their is a valid recipe again
  const img = document.getElementById("output-image");
  img.style.opacity = '0';

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

// Function that we can call from both seeRecipe() and submitGrid()
function processGridInput() {
  // Making a copy of the crafting table grid and the items in it
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
  return trimmedGrid
}

// Sends grid to backend to confirm if pattern in grid is an accepted recipe
// If recipe is valid, display image of craftable item in frontend
function seeRecipe() {
  trimmedGrid = processGridInput()

  // Send to server
  fetch('/check-craft-result', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ grid: trimmedGrid })
  })
  .then(res => res.json())
  // Display craftable item
  .then(data => {
    // console.log("SERVER RESPONSE:", data); // Debugging
    if (data.success && data.crafted_item) {
      const img = document.getElementById("output-image");
      img.src = `/static/items/${data.crafted_item}.png`;
      img.style.display = "block";
      // Making crafting output visible again
      img.style.opacity = '1';
    }
  })
  .catch(err => console.error('Error:', err));
}

// Sends grid to backend to confirm if pattern in grid is the correct answer
function submitGrid() {
  // Going through grid, and filling out grid data array
  trimmedGrid = processGridInput()

  // Send to server
  fetch('/check-answer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ grid: trimmedGrid })
  })
  .then(res => res.json()) // idk what this does
  .then(data => {
    // console.log("SERVER RESPONSE:", data); // Debugging
    if (data.correct === true) { // Displays a win screen, then refreshes the page
      showWinScreen(data.crafted_item)  // Why is there no ";" at the end of this line - is that why the code is weird?
      setTimeout(() => {
        window.location.reload();
      }, 2000); // Kind of delicate. If some code is wrong, this doesn't trigger?
      return;
    }

    // Now we can do stuff with all of the info it sends back
    // if guess was correct, add a point in infinite mode
    
    // if guess was valid but incorrect, add miniature grid of that guess to our history display
    if (data.success) {
      console.log(data.answerPattern)
      console.log(data.answer); // Debugging
      // console.log("Incorrect item"); // Debugging
      
      // ***Remake the current crafting table (but mini) and then append it to vertical-flexbox-2
      const newCraftingTable = document.createElement("div");
      newCraftingTable.id = "miniCraftingTable"; // New version of <div class="box grid-wrapper" id="craftingTable">
      const newGrid = document.createElement("div");
      newGrid.id = "miniGrid" // New version of <div class="grid" id="grid">
      // New cells
      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
          // New cells
          const cell = document.createElement("div");
          cell.classList.add("miniGridCell");
          
          // Access the original cell that has data-row of i and data-col of j
          const origCell = document.querySelector(`.cell[data-row="${i}"][data-col="${j}"]`);   // console.log(origCell.dataset.row);   // console.log(origCell.dataset.col); // Debugging
          // If origCell contains an image, add the same image to the mini crafting table
          if (origCell.hasChildNodes()) {   // Child node will be a div if it contains an image / item
            const newImg = document.createElement("img");
            newImg.classList.add("miniGridItem");
            // Set the src attribute
            newImg.src = origCell.querySelector('img').src;   // console.log(newImg.src); // Debugging
            newImg.setAttribute("draggable", "false");
            cell.append(newImg);
          }
          // Check if an item is in the correct answers - green if it is, red if not
          // Get item
          const item = origCell.querySelector('.item');
          if (item != null) {
            console.log(item); // Debugging
            console.log(item.dataset.id); // Debugging
            // Check if item.dataset.id (string) is in data.answerPattern (array of arrays of strings)
            if (data.answerPattern.some(innerArray => innerArray.includes(item.dataset.id)) ) {   // used kind of shitty ai code for if condition
              // console.log("Item included in recipe"); // Debugging
              cell.style.backgroundColor = "#00ff00";
            }
            else {
              cell.style.backgroundColor = "#ff0000";
            }
          }
          newGrid.appendChild(cell);
        }
      }      
      // These "boxes" are essentially just cells but outside of the 3x3 grid:
      const newArrowBox = document.createElement("div");
      newArrowBox.id = "miniArrowBox";
      // Arrow image
      const newArrowBoxImg = document.createElement("img"); // New version of <img src="/static/CT-Arrow.png"/>
      newArrowBoxImg.id = "miniArrowBoxImg";
      newArrowBoxImg.src = "/static/CT-Arrow.png";
      newArrowBox.append(newArrowBoxImg);

      const newOutputBox = document.createElement("div");
      newOutputBox.id = "miniOutputBox";
      // Output image
      const origOutputBox = document.querySelector('.output-box');   // Should've used an Id instead of a class in the original html - could then just use document.getElementByID() instead of querySelector()
      const newOutputImg = document.createElement("img");
      newOutputImg.id = "miniOutputItem";
      newOutputImg.src = origOutputBox.querySelector('img').src;
      newOutputImg.setAttribute("draggable", "false");
      newOutputBox.append(newOutputImg);

      // Add all of the components into the new crafting table, then add the new crafting table to our history column
      newCraftingTable.append(newGrid);
      newCraftingTable.append(newArrowBox);
      newCraftingTable.append(newOutputBox);
      const pastGuessView = document.getElementById('vertical-flexbox-2');
      pastGuessView.append(newCraftingTable);

      // Clear the grid after the user submits their guess
      clearGrid();      
    }
  })
  .catch(err => console.error('Error:', err));
}

function showWinScreen(crafted_item) {
  winDiv = document.getElementById("winScreen");
  winDiv.style.display = "flex";
  winDiv.innerHTML = `Correct! The item was&nbsp<b>${crafted_item}</b>! Starting a new game...`;
}